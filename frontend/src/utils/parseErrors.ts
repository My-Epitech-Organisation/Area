export function parseErrors(errBody: any): { message: string; fields?: Record<string, string[]> } {
  if (!errBody)
    return { message: 'An error occurred' };
  if (typeof errBody === 'string')
    return { message: errBody };
  if (errBody && typeof errBody === 'object' && 'detail' in errBody)
    return { message: String((errBody as any).detail) };
  if (typeof errBody === 'object') {
    const fields: Record<string, string[]> = {};
    const parts: string[] = [];
    for (const k of Object.keys(errBody)) {
      const v = errBody[k];
      if (Array.isArray(v)) {
        fields[k] = v.map((s) => String(s));
        parts.push(`${k}: ${v.join(' ')}`);
      } else if (typeof v === 'string') {
        fields[k] = [v];
        parts.push(`${k}: ${v}`);
      }
    }
    return { message: parts.join(' — '), fields };
  }
  return { message: 'An error occurred' };
}

export default parseErrors;
