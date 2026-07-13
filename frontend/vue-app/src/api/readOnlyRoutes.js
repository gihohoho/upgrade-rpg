export const API_READONLY_METHOD = 'GET';

export const ADMIN_READONLY_ROUTES = Object.freeze({
  requirements: '/admin/requirements',
  overview: '/admin/overview',
  saveSnapshots: '/admin/save-snapshots',
  masterDomains: '/admin/master-data/domains',
  masterCatalog: '/admin/master-data/catalog',
  masterCreateBlueprint: '/admin/master-data/create-blueprint',
  masterDetail: '/admin/master-data/detail',
  masterRelations: '/admin/master-data/relations',
  changeLogs: '/admin/change-logs',
  changeLogDetail: '/admin/change-logs/{changeLogId}',
});

export const GAME_READONLY_ROUTES = Object.freeze({
  masterData: '/game/master-data',
  load: '/game/load',
  saveSlots: '/game/save-slots',
});

export const HEALTH_READONLY_ROUTES = Object.freeze({
  health: '/health',
  dbHealth: '/health/db',
});

export const READONLY_ROUTE_GROUPS = Object.freeze({
  admin: ADMIN_READONLY_ROUTES,
  game: GAME_READONLY_ROUTES,
  health: HEALTH_READONLY_ROUTES,
});

export function fillRouteParams(path, params = {}) {
  return Object.entries(params).reduce((nextPath, [key, value]) => {
    return nextPath.replace(`{${key}}`, encodeURIComponent(String(value)));
  }, path);
}
