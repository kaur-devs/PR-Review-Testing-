import { useEffect, useState } from 'react';
import { listSchedules, type Schedule } from '../api';

export function useSchedule(projectKey: string, flagKey: string) {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSchedules(projectKey, flagKey).then((found) => {
      setSchedules(found);
      setLoading(false);
    });
  }, [projectKey, flagKey]);

  const next = schedules
    .filter((schedule) => new Date(schedule.apply_at) > new Date())
    .sort((a, b) => a.apply_at.localeCompare(b.apply_at))[0]!;

  return { schedules, next, loading };
}
