/**
 * Formatting helpers.
 *
 * Dates are formatted from their ISO parts rather than through `Intl` with a
 * runtime locale, so the server and the client always produce the same string
 * and never trigger a hydration mismatch.
 */

const MONTHS_LONG = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
] as const;

const MONTHS_SHORT = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
] as const;

function parts(iso: string): [number, number, number] | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  if (!match) return null;
  const [, y, m, d] = match;
  const month = Number(m);
  if (month < 1 || month > 12) return null;
  return [Number(y), month, Number(d)];
}

/** `2026-09-10` → `10 September 2026`. For prose and record headers. */
export function formatDate(iso: string): string {
  const p = parts(iso);
  if (!p) return iso;
  const [year, month, day] = p;
  return `${day} ${MONTHS_LONG[month - 1]} ${year}`;
}

/** `2026-09-10` → `10 Sep 2026`. For dense tables. */
export function formatDateShort(iso: string): string {
  const p = parts(iso);
  if (!p) return iso;
  const [year, month, day] = p;
  return `${String(day).padStart(2, "0")} ${MONTHS_SHORT[month - 1]} ${year}`;
}

/** Unchanged ISO date, for mono metadata lines where sorting matters visually. */
export function formatDateIso(iso: string): string {
  return parts(iso) ? iso.slice(0, 10) : iso;
}

/** `1` → `1 source`, `4` → `4 sources`. Counts always carry their noun. */
export function pluralise(count: number, singular: string, plural?: string) {
  return `${count} ${count === 1 ? singular : (plural ?? `${singular}s`)}`;
}
