#!/usr/bin/env node

import {
  copyFile,
  mkdir,
  readdir,
  readFile,
  rm,
  stat,
} from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDirectory, "..");
const outputDirectory = path.resolve(projectRoot, "frontend", "legacy-dist");
const expectedOutputDirectory = path.join(projectRoot, "frontend", "legacy-dist");
const sourceDirectory = path.join(projectRoot, "src");
const entrypoints = ["index.html", "admin.html"];
const publishedExtensions = new Set([".js", ".css"]);
const forbiddenTextPatterns = [
  /\bpostgres(?:ql)?\:\/\//i,
  /\bnpg_[a-z0-9]+\b/i,
  /\bghp_[a-z0-9]+\b/i,
  /\bgithub_pat_[a-z0-9_]+\b/i,
  /\bep-[a-z0-9-]+\.(?:c-\d+\.)?ap-southeast-1\.aws\.neon\.tech\b/i,
];

function fail(message) {
  throw new Error(`legacy static build refused: ${message}`);
}

async function copyRuntimeFiles(source, destination) {
  const entries = await readdir(source, { withFileTypes: true });
  for (const entry of entries) {
    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);
    if (entry.isSymbolicLink()) {
      fail(`symbolic link is not allowed: ${path.relative(projectRoot, sourcePath)}`);
    }
    if (entry.isDirectory()) {
      await copyRuntimeFiles(sourcePath, destinationPath);
      continue;
    }
    if (!entry.isFile() || !publishedExtensions.has(path.extname(entry.name).toLowerCase())) {
      continue;
    }
    await mkdir(path.dirname(destinationPath), { recursive: true });
    await copyFile(sourcePath, destinationPath);
  }
}

function referencedLocalAssets(html) {
  const references = [];
  const pattern = /(?:src|href)=["']([^"'?#]+)(?:[?#][^"']*)?["']/gi;
  for (const match of html.matchAll(pattern)) {
    const reference = match[1];
    if (/^(?:https?:|data:|#|\/\/)/i.test(reference)) continue;
    references.push(reference);
  }
  return references;
}

async function collectFiles(directory) {
  const files = [];
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) {
      fail(`output contains a symbolic link: ${path.relative(outputDirectory, absolutePath)}`);
    }
    if (entry.isDirectory()) files.push(...await collectFiles(absolutePath));
    else if (entry.isFile()) files.push(absolutePath);
  }
  return files;
}

async function verifyOutput() {
  const topLevel = (await readdir(outputDirectory)).sort();
  const expectedTopLevel = ["admin.html", "index.html", "src"];
  if (JSON.stringify(topLevel) !== JSON.stringify(expectedTopLevel)) {
    fail(`unexpected output entries: ${topLevel.join(", ")}`);
  }

  for (const entrypoint of entrypoints) {
    const htmlPath = path.join(outputDirectory, entrypoint);
    const html = await readFile(htmlPath, "utf8");
    for (const reference of referencedLocalAssets(html)) {
      const target = path.resolve(outputDirectory, reference);
      if (!target.startsWith(`${outputDirectory}${path.sep}`)) {
        fail(`${entrypoint} references a path outside the output directory`);
      }
      try {
        if (!(await stat(target)).isFile()) fail(`${entrypoint} reference is not a file: ${reference}`);
      } catch {
        fail(`${entrypoint} references a missing file: ${reference}`);
      }
    }
  }

  const files = await collectFiles(outputDirectory);
  let totalBytes = 0;
  for (const file of files) {
    const content = await readFile(file);
    totalBytes += content.byteLength;
    const text = content.toString("utf8");
    if (forbiddenTextPatterns.some((pattern) => pattern.test(text))) {
      fail(`secret- or database-endpoint-shaped text found in ${path.relative(outputDirectory, file)}`);
    }
  }
  return { fileCount: files.length, totalBytes };
}

async function main() {
  if (outputDirectory !== expectedOutputDirectory) {
    fail("output directory safety boundary changed");
  }
  await rm(outputDirectory, { recursive: true, force: true });
  await mkdir(outputDirectory, { recursive: true });
  for (const entrypoint of entrypoints) {
    await copyFile(path.join(projectRoot, entrypoint), path.join(outputDirectory, entrypoint));
  }
  await copyRuntimeFiles(sourceDirectory, path.join(outputDirectory, "src"));
  const result = await verifyOutput();
  console.log("legacy static site build complete");
  console.log(`- output: ${path.relative(projectRoot, outputDirectory).replaceAll("\\", "/")}`);
  console.log(`- files/bytes: ${result.fileCount}/${result.totalBytes}`);
  console.log("- secrets or database credentials included: no");
}

await main();
