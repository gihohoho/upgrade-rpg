import { requestReadOnly } from './readOnlyClient';
import { ADMIN_READONLY_ROUTES, fillRouteParams } from './readOnlyRoutes';

export const adminReadOnlyApi = Object.freeze({
  fetchRequirements(options) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.requirements, options);
  },

  fetchOverview(options) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.overview, options);
  },

  fetchSaveSnapshots({ limit = 30, sort = 'updated_desc', ...query } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.saveSnapshots, {
      ...options,
      query: { limit, sort, ...query },
    });
  },

  fetchMasterDomains(options) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.masterDomains, options);
  },

  fetchMasterCatalog({ domain, limit = 20, page = 1, sort = 'id_asc', ...query } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.masterCatalog, {
      ...options,
      query: { domain, limit, page, sort, ...query },
    });
  },

  fetchMasterCreateBlueprint({ domain } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.masterCreateBlueprint, {
      ...options,
      query: { domain },
    });
  },

  fetchMasterDetail({ domain, rowId } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.masterDetail, {
      ...options,
      query: { domain, id: rowId },
    });
  },

  fetchMasterRelations({ domain, rowId, limit = 50 } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.masterRelations, {
      ...options,
      query: { domain, id: rowId, limit },
    });
  },

  fetchChangeLogs({ limit = 30, sort = 'created_desc', ...query } = {}, options = {}) {
    return requestReadOnly(ADMIN_READONLY_ROUTES.changeLogs, {
      ...options,
      query: { limit, sort, ...query },
    });
  },

  fetchChangeLogDetail({ changeLogId } = {}, options = {}) {
    return requestReadOnly(fillRouteParams(ADMIN_READONLY_ROUTES.changeLogDetail, { changeLogId }), options);
  },
});
