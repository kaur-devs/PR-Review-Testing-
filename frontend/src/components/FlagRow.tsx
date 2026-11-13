import type { Flag } from '../types';

interface Props {
  flag: Flag;
}

export default function FlagRow({ flag }: Props) {
  return (
    <tr className="border-b border-slate-800">
      <td className="px-3 py-2">
        <code className="text-sm text-sky-300">{flag.key}</code>
        {flag.description && (
          <p className="mt-0.5 text-xs text-slate-500">{flag.description}</p>
        )}
      </td>
      <td className="px-3 py-2">
        <span
          className={
            flag.enabled
              ? 'rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-300'
              : 'rounded-full bg-slate-700/40 px-2 py-0.5 text-xs text-slate-400'
          }
        >
          {flag.enabled ? 'on' : 'off'}
        </span>
      </td>
      <td className="px-3 py-2 text-sm tabular-nums text-slate-300">
        {flag.rollout_percent}%
      </td>
      <td className="px-3 py-2 text-xs text-slate-500">
        {flag.rules.length === 0
          ? 'everyone'
          : `${flag.rules.length} rule${flag.rules.length === 1 ? '' : 's'}`}
      </td>
    </tr>
  );
}
