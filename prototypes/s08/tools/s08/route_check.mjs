// Validate the documented per-project entry against the standard projected lookup.
// The projection uses the canonical path as its key and removes the internal _key field.
export function ownedRoute(project, cwd, projected, entry) {
  if (project !== cwd || entry?._key !== project) throw new Error('canonical owned project mismatch');
  if (!projected) return false; // Startup publication is bounded by the supervisor deadline.
  for (const field of ['pid', 'port', 'token_path']) {
    if (projected[field] !== entry[field]) return false;
  }
  return true;
}
