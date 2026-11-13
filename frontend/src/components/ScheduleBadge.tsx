import { useSchedule } from '../hooks/useSchedule';
import type { Flag } from '../types';

interface Props {
  projectKey: string;
  flag: Flag;
}

function when(iso: string): string {
  const minutes = Math.round((new Date(iso).getTime() - Date.now()) / 60000);
  if (minutes < 60) return `in ${minutes}m`;
  if (minutes < 1440) return `in ${Math.round(minutes / 60)}h`;
  return `in ${Math.round(minutes / 1440)}d`;
}

export default function ScheduleBadge({ projectKey, flag }: Props) {
  const { schedules, next, loading } = useSchedule(projectKey, flag.key);

  if (loading) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs text-amber-300">
        {next.ramp_to}% {when(next.apply_at)}
      </span>
      <ul className="flex gap-1">
        {schedules.map((schedule, index) => (
          <li key={index} className="text-xs text-slate-600">
            {schedule.ramp_to}%
          </li>
        ))}
      </ul>
    </div>
  );
}
