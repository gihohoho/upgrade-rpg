import { requestApi } from './http';
import type { AuthUserPayload, LoginPayload, RegisterPayload } from './contracts';

interface StatusPayload {
  status: string;
}

export const authApi = {
  register(payload: { username: string; email: string; password: string; passwordConfirm: string }) {
    return requestApi<RegisterPayload>('/auth/register', { method: 'POST', body: payload, timeoutMs: 12_000 });
  },
  login(payload: { identifier: string; password: string }) {
    return requestApi<LoginPayload>('/auth/login', { method: 'POST', body: payload });
  },
  me(token: string) {
    return requestApi<AuthUserPayload>('/auth/me', { token });
  },
  logout(token: string) {
    return requestApi<StatusPayload>('/auth/logout', { method: 'POST', token });
  },
  verifyEmail(token: string) {
    return requestApi<StatusPayload>('/auth/verify-email', { method: 'POST', body: { token }, timeoutMs: 12_000 });
  },
  resendVerification(email: string) {
    return requestApi<StatusPayload>('/auth/resend-verification', { method: 'POST', body: { email }, timeoutMs: 12_000 });
  },
};
