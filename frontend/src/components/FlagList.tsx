import FlagRow from './FlagRow';
import { useFlags } from '../hooks/useFlags';

interface Props {
  projectKey: string;
}

export default function FlagList({ projectKey }: Props) {
  const { flags, loading, error } = useFlags(projectKey);

  if (loading) return <p className="p-6 text-sm text-slate-500">Loading…</p>;
  if (error) return <p className="p-6 text-sm text-rose-400">{error}</p>;
  if (flags.length === 0) {
    return <p className="p-6 text-sm text-slate-500">No flags yet.</p>;
  }

  return (
    <table className="w-full text-left">
      <thead>
        <tr className="border-b border-slate-800 text-xs uppercase text-slate-500">
          <th className="px-3 py-2 font-medium">Flag</th>
          <th className="px-3 py-2 font-medium">State</th>
          <th className="px-3 py-2 font-medium">Rollout</th>
          <th className="px-3 py-2 font-medium">Targeting</th>
        </tr>
      </thead>
      <tbody>
        {flags.map((flag) => (
          <FlagRow key={flag.id} flag={flag} />
        ))}
      </tbody>
    </table>
  );
}
