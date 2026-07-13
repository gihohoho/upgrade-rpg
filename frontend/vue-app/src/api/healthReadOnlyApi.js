import { requestReadOnly } from './readOnlyClient';
import { HEALTH_READONLY_ROUTES } from './readOnlyRoutes';

export const healthReadOnlyApi = Object.freeze({
  fetchHealth(options) {
    return requestReadOnly(HEALTH_READONLY_ROUTES.health, options);
  },

  fetchDbHealth(options) {
    return requestReadOnly(HEALTH_READONLY_ROUTES.dbHealth, options);
  },
});
