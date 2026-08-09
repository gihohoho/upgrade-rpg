#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const HTML = fs.readFileSync(path.join(ROOT, "admin.html"), "utf8");
const MODULE_SOURCE = fs.readFileSync(path.join(ROOT, "src/api/admin/admin-account-management.js"), "utf8");
const ENTRY_SOURCE = fs.readFileSync(path.join(ROOT, "src/api/admin-page-readonly.js"), "utf8");
const CLIENT_SOURCE = fs.readFileSync(path.join(ROOT, "src/api/game-api-client.js"), "utf8");
const AUTH_SOURCE = fs.readFileSync(path.join(ROOT, "src/api/auth-session.js"), "utf8");
const CSS_SOURCE = fs.readFileSync(path.join(ROOT, "src/styles/account-admin.css"), "utf8");

function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function createClassList() {
  const values = new Set();
  return {
    add(...names) { names.forEach((name) => values.add(name)); },
    remove(...names) { names.forEach((name) => values.delete(name)); },
    toggle(name, force) {
      if (force === true) values.add(name);
      else if (force === false) values.delete(name);
      else if (values.has(name)) values.delete(name);
      else values.add(name);
    },
    contains(name) { return values.has(name); },
  };
}

function createElement() {
  const attributes = new Map();
  return {
    hidden: false,
    value: "",
    disabled: false,
    dataset: {},
    innerHTML: "",
    textContent: "",
    classList: createClassList(),
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.get(name) || null; },
    focus() {},
    matches() { return false; },
    closest() { return null; },
    querySelector() { return null; },
  };
}

function createStorage() {
  const values = new Map();
  return {
    getItem(key) { return values.has(String(key)) ? values.get(String(key)) : null; },
    setItem(key, value) { values.set(String(key), String(value)); },
    removeItem(key) { values.delete(String(key)); },
  };
}

function createHarness(options) {
  const elements = new Map();
  const selectors = [
    "[data-account-admin-gate]",
    "[data-account-admin-content]",
    "[data-account-admin-bootstrap]",
    "[data-account-admin-gate-message]",
    "[data-account-admin-current-admin]",
    "[data-account-admin-status-line]",
    "[data-account-admin-user-table]",
    "[data-account-admin-summary]",
    "[data-account-admin-pagination]",
    "[data-account-admin-query]",
    "[data-account-admin-status]",
    "[data-account-admin-sort]",
    "[data-account-admin-detail-modal]",
    "[data-account-admin-detail-body]",
    "[data-account-admin-detail-title]",
    "[data-account-admin-status-modal]",
  ];
  selectors.forEach((selector) => elements.set(selector, createElement()));
  elements.get("[data-account-admin-status]").value = "all";
  elements.get("[data-account-admin-sort]").value = "created_desc";

  const calls = [];
  let legacyBoots = 0;
  const document = {
    readyState: "complete",
    body: createElement(),
    activeElement: createElement(),
    querySelector(selector) { return elements.get(selector) || null; },
    addEventListener() {},
  };
  const malicious = '\"><img src=x onerror="window.pwned=1">';
  const gameApi = {
    request() { throw new Error("raw request fallback should not be needed in this smoke"); },
    async fetchAccountBootstrapStatus() {
      calls.push("bootstrap-status");
      return {
        payload: {
          currentUser: { id: 7, username: malicious, isAdmin: options.isAdmin },
          canBootstrap: false,
        },
      };
    },
    async listAdminAccounts() {
      calls.push("users");
      return {
        payload: {
          page: 1,
          totalPages: 1,
          count: 1,
          total: 1,
          users: [{
            id: 7,
            username: malicious,
            isActive: true,
            isAdmin: true,
            characterSlotsUsed: 1,
            characterSlotCapacity: 8,
            createdAt: "2026-08-10T00:00:00Z",
          }],
        },
      };
    },
    async fetchAdminAccountDetail(userId) {
      calls.push(`detail:${userId}`);
      return {
        payload: {
          user: {
            id: userId,
            username: malicious,
            isActive: true,
            isAdmin: true,
            characterSlotsUsed: 1,
            characterSlotCapacity: 8,
            createdAt: "2026-08-10T00:00:00Z",
          },
          characterSlots: [{
            slotIndex: 1,
            isEmpty: false,
            name: malicious,
            characterCode: "weapon_master",
            level: 1,
            lastSavedAt: "2026-08-10T00:00:00Z",
          }],
        },
      };
    },
  };
  const context = {
    console,
    Date,
    Intl,
    Promise,
    setTimeout,
    clearTimeout,
    document,
    RpgGameApi: gameApi,
    RpgAuthSession: {
      restoreTokenFromStorage() { calls.push("restore-token"); return "stored-token"; },
    },
    RpgAdminReadOnlyPage: {
      bootAdminReadOnlyPage() {
        calls.push("legacy-admin-boot");
        legacyBoots += 1;
      },
    },
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(MODULE_SOURCE, context, { filename: "admin-account-management.js" });
  return { context, elements, calls, malicious, getLegacyBoots: () => legacyBoots };
}

async function settle() {
  await new Promise((resolve) => setTimeout(resolve, 10));
}

async function testRuntimeGateAndEscaping() {
  const nonAdmin = createHarness({ isAdmin: false });
  await settle();
  requireCondition(
    JSON.stringify(nonAdmin.calls) === JSON.stringify(["restore-token", "bootstrap-status"]),
    `non-admin page called protected APIs before authorization: ${nonAdmin.calls.join(", ")}`,
  );
  requireCondition(nonAdmin.getLegacyBoots() === 0, "legacy admin page booted for a non-admin account");
  requireCondition(
    nonAdmin.elements.get("[data-account-admin-content]").getAttribute("aria-hidden") === "true",
    "admin content was not kept locked for a non-admin account",
  );

  const admin = createHarness({ isAdmin: true });
  await settle();
  requireCondition(
    JSON.stringify(admin.calls.slice(0, 4)) === JSON.stringify(["restore-token", "bootstrap-status", "users", "legacy-admin-boot"]),
    `admin unlock call order changed: ${admin.calls.join(", ")}`,
  );
  requireCondition(admin.getLegacyBoots() === 1, "authorized legacy admin page did not boot exactly once");
  const tableHtml = admin.elements.get("[data-account-admin-user-table]").innerHTML;
  requireCondition(!tableHtml.includes("<img src=x"), "server username was inserted into list HTML without escaping");
  requireCondition(tableHtml.includes("&lt;img src=x"), "escaped server username is missing from list HTML");

  await admin.context.RpgAdminAccountManagement.openUserDetail(7, createElement());
  const detailHtml = admin.elements.get("[data-account-admin-detail-body]").innerHTML;
  requireCondition(!detailHtml.includes("<img src=x"), "server character name was inserted into detail HTML without escaping");
  requireCondition(detailHtml.includes("&lt;img src=x"), "escaped server character name is missing from detail HTML");
  requireCondition(
    admin.elements.get("[data-account-admin-detail-title]").textContent.includes(admin.malicious),
    "detail title should use textContent for the server username",
  );
}

function testStaticContract() {
  const authScriptIndex = HTML.indexOf('src/api/auth-session.js?v=370');
  const clientScriptIndex = HTML.indexOf('src/api/game-api-client.js?v=370');
  const accountScriptIndex = HTML.indexOf('src/api/admin/admin-account-management.js?v=370');
  const legacyScriptIndex = HTML.indexOf('src/api/admin-page-readonly.js?v=370');
  requireCondition(authScriptIndex >= 0 && authScriptIndex < clientScriptIndex, "admin page does not load auth session before API client");
  requireCondition(accountScriptIndex >= 0 && accountScriptIndex < legacyScriptIndex, "account authorization gate must load before legacy admin entry");
  requireCondition(HTML.includes('data-account-admin-content aria-hidden="true"'), "admin content is not fail-closed in HTML");
  requireCondition(HTML.includes('src/styles/account-admin.css?v=370'), "separate account-admin stylesheet missing");
  requireCondition(CSS_SOURCE.includes("@media (max-width: 680px)"), "account admin mobile layout missing");
  requireCondition(CSS_SOURCE.includes("prefers-reduced-motion"), "account admin reduced-motion fallback missing");

  const bootBlock = ENTRY_SOURCE.split("function bootAdminReadOnlyPage()", 2)[1].split("function checkAdminReadOnlyPageReady", 1)[0];
  requireCondition(bootBlock.includes("!accountGuard"), "missing account guard is not fail-closed");
  requireCondition(bootBlock.includes('typeof accountGuard.isAdminAuthorized !== "function"'), "invalid account guard is not fail-closed");
  requireCondition(bootBlock.includes("accountGuard.isAdminAuthorized() !== true"), "admin authorization does not require exact true");
  requireCondition(bootBlock.indexOf("isAdminAuthorized") < bootBlock.indexOf("refreshAdminReadOnlyPage"), "legacy admin API guard runs too late");
  requireCondition(MODULE_SOURCE.includes("escapeHtml(user.username)"), "member username HTML escaping missing");
  requireCondition(MODULE_SOURCE.includes("escapeHtml(slot.name"), "character name HTML escaping missing");
  requireCondition(!/\b(?:alert|confirm)\s*\(/.test(MODULE_SOURCE), "browser alert/confirm is used instead of the custom modal");

  requireCondition(CLIENT_SOURCE.includes("...(requestOptions.auth === false ? {} : getAuthHeaders())"), "Bearer auth is not attached by default");
  requireCondition(MODULE_SOURCE.includes("fetchAccountBootstrapStatus"), "bootstrap-status API wrapper missing");
  const initializeBlock = MODULE_SOURCE.slice(MODULE_SOURCE.indexOf("function initialize()"), MODULE_SOURCE.indexOf("window.RpgAdminAccountManagement"));
  requireCondition(initializeBlock.indexOf("restoreTokenFromStorage") < initializeBlock.indexOf("return checkAdminGate()"), "stored token is not restored before the first admin gate request");
  requireCondition(MODULE_SOURCE.includes("fetchAdminAccountDetail(userId, { timeoutMs: 5000 })"), "detail wrapper contract mismatch");
  requireCondition(MODULE_SOURCE.includes("previewAdminAccountStatus(target.userId, payload, { timeoutMs: 5000 })"), "status preview wrapper contract mismatch");
  requireCondition(MODULE_SOURCE.includes("applyAdminAccountStatus(target.userId, payload, { timeoutMs: 5000 })"), "status apply wrapper contract mismatch");

  const visibleSources = `${HTML}\n${MODULE_SOURCE}`;
  for (const forbidden of ["passwordHash", "password_hash", "accessToken", "access_token", "snapshot_json"]) {
    requireCondition(!visibleSources.includes(forbidden), `sensitive field marker reached admin DOM/module: ${forbidden}`);
  }
}

async function testStoredTokenAuthorization() {
  const localStorage = createStorage();
  const sessionStorage = createStorage();
  const calls = [];
  const context = {
    console,
    URL,
    AbortController,
    localStorage,
    sessionStorage,
    setTimeout,
    clearTimeout,
    async fetch(url, options) {
      calls.push({ url: String(url), options });
      return { ok: true, status: 200, async json() { return { ok: true, payload: { currentUser: { id: 7, username: "owner", isAdmin: true } } }; } };
    },
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(AUTH_SOURCE, context, { filename: "auth-session.js" });
  vm.runInContext(CLIENT_SOURCE, context, { filename: "game-api-client.js" });
  localStorage.setItem(context.RpgAuthSession.ACCESS_TOKEN_KEY, "persisted-admin-token");
  requireCondition(context.RpgAuthSession.getAccessToken() === "", "admin new-tab harness did not begin with empty in-memory token");
  context.RpgAuthSession.restoreTokenFromStorage();
  await context.RpgGameApi.fetchAccountBootstrapStatus({ timeoutMs: 0 });
  requireCondition(calls.length === 1, "admin bootstrap integration did not issue exactly one request");
  requireCondition(calls[0].options.headers.Authorization === "Bearer persisted-admin-token", "stored admin token did not reach Authorization header");
}

function testMissingGuardDoesNotBootLegacyApis() {
  const bootStart = ENTRY_SOURCE.indexOf("let authenticatedAdminPageBooted = false;");
  const bootEnd = ENTRY_SOURCE.indexOf("function checkAdminReadOnlyPageReady", bootStart);
  requireCondition(bootStart >= 0 && bootEnd > bootStart, "legacy admin boot block was not found");
  const exactBootSource = ENTRY_SOURCE.slice(bootStart, bootEnd);
  const calls = [];
  const context = {
    window: {},
    bindEvents() { calls.push("bind-events"); },
    initializeAdminLayoutShell() { calls.push("layout"); },
    syncLocationHints() { calls.push("location"); },
    syncApiInput() { calls.push("api-input"); },
    syncAdminWriteDevKeyInput() { calls.push("dev-key"); },
    resetSnapshotFilters() { calls.push("snapshot-filter"); },
    resetMasterCatalogFilters() { calls.push("master-filter"); },
    resetChangeLogFilters() { calls.push("log-filter"); },
    renderMasterDetail() { calls.push("detail-render"); },
    renderAdminCreateBlueprint() { calls.push("create-render"); },
    renderAdminJsSplitReadiness() { calls.push("readiness-render"); },
    refreshAdminReadOnlyPage() { calls.push("protected-admin-fetch"); },
  };
  vm.createContext(context);
  vm.runInContext(`${exactBootSource}\nwindow.__bootResult = bootAdminReadOnlyPage();`, context);
  requireCondition(context.window.__bootResult === false, "missing account guard did not stop legacy boot");
  requireCondition(calls.length === 0, `missing account guard triggered legacy work: ${calls.join(", ")}`);
}

async function main() {
  testStaticContract();
  testMissingGuardDoesNotBootLegacyApis();
  await testStoredTokenAuthorization();
  await testRuntimeGateAndEscaping();
  console.log("OK: v370 authenticated admin account UI smoke passed");
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : error);
  process.exitCode = 1;
});
