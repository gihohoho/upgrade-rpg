const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("backend/app/api/routes/admin.py", [
  "limit: int = Query(default=20",
  "page: int = Query(default=1",
  "sort: str = Query(default=\"id_asc\"",
  "page=page",
  '"totalPages": catalog["totalPages"]',
]);

assertContains("backend/app/services/admin_service.py", [
  "limit: int = 20",
  "page: int = 1",
  "safe_offset = (safe_page - 1) * safe_limit",
  ".offset(safe_offset).limit(safe_limit)",
  '"totalPages": total_pages',
  '"hasNextPage": safe_page < total_pages',
]);

assertContains("src/api/game-api-client.js", [
  "const page = opts.page !== undefined ? Number(opts.page) : undefined",
  "page,",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v138.admin-safe-apply-review",
  "const DEFAULT_MASTER_LIMIT = 20",
  'const DEFAULT_MASTER_SORT = "id_asc"',
  "data-admin-master-page",
  "renderMasterCatalogPagination",
  "refreshMasterCatalogWithPage",
  "master-catalog-prev-page",
  "master-catalog-next-page",
]);

assertContains("admin.html", [
  "data-admin-master-page",
  "data-admin-master-catalog-pagination",
  "catalog-pagination",
  '<option value="20" selected>20</option>',
  '<option value="id_asc" selected>ID순</option>',
]);

console.log("admin master catalog pagination smoke test passed");
