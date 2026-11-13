import FlagList from './components/FlagList';

export default function App() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-base font-semibold">Flagpole</h1>
        <p className="mt-0.5 text-xs text-slate-500">
          Feature flags with percentage rollouts and attribute targeting
        </p>
      </header>
      <FlagList projectKey="demo" />
    </main>
  );
}
