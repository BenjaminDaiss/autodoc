/**
 * Base API client.
 * In development the React proxy (package.json "proxy") forwards /api/* to
 * localhost:8000, so we use a relative base URL.  In production the FastAPI
 * server can serve the built React app and both sit on the same origin.
 */

const BASE = '';   // relative – works with CRA proxy and same-origin production

async function request(method, path, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== null) {
    options.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, options);
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Request failed: ${res.status}`);
  }
  return data;
}

export const api = {
  get:    (path)         => request('GET',    path),
  post:   (path, body)   => request('POST',   path, body),
  put:    (path, body)   => request('PUT',    path, body),
  delete: (path)         => request('DELETE', path),
};
