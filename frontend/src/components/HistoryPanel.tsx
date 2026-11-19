import { useHistory } from '../hooks/useHistory';
import type { FlagChange } from '../types';

interface Props {
  projectKey: string;
}

export default function HistoryPanel({ projectKey }: Props) {
  const { history, loading } = useHistory(projectKey);

  if (loading) {
    return <p className="px-6 py-4 text-sm text-slate-500">Loading history…</p>;
  }
  if (!history) return null;

  // Description edits are noise in a changelog; the rollout moves are not.
  const interesting = history.changes.filter(
    (change) => change.field !== 'description',
  );

  const byFlag = new Map<string, FlagChange[]>();
  for (const change of interesting) {
    byFlag.set(change.flag_key, [...(byFlag.get(change.flag_key) ?? []), change]);
  }

  return (
    <section className="border-t border-slate-800 px-6 py-5">
      <h2 className="text-sm font-semibold">Recent changes</h2>
      <p className="mt-0.5 text-xs text-slate-500">{history.summary}</p>

      {[...byFlag.entries()].map(([flagKey, changes]) => (
        <div key={flagKey} className="mt-4">
          <code className="text-sm text-sky-300">{flagKey}</code>
          <ul className="mt-1 space-y-1">
            {changes.map((change, index) => (
              <li key={index} className="text-xs text-slate-400">
                {change.field}: {change.before} → {change.after}
                <span className="ml-2 text-slate-600">
                  v{change.version} · {change.actor} ·{' '}
                  {new Date(change.changed_at).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
