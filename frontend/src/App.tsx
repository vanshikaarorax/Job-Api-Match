import { FormEvent, useState } from "react";
import { api, Candidate, Job, Recommendation } from "./api";

const splitSkills = (value: string) => value.split(",").map((skill) => skill.trim()).filter(Boolean);
const messageFor = (error: unknown) => error instanceof Error ? error.message : "Something went wrong. Please try again.";

function ScoreBreakdown({ recommendation }: { recommendation: Recommendation }) {
  const { skills, experience, location, salary } = recommendation.breakdown;
  return <div className="breakdown">
    <div><span>Skills</span><strong>{skills.score} / {skills.max}</strong></div>
    <small>Must-have: {skills.mustHave.matched} / {skills.mustHave.total} · Nice-to-have: {skills.niceToHave.matched} / {skills.niceToHave.total}</small>
    <div><span>Experience</span><strong>{experience.score} / {experience.max}</strong></div>
    <div><span>Location <em>({location.reason.replace("_", " ")})</em></span><strong>{location.score} / {location.max}</strong></div>
    <div><span>Salary</span><strong>{salary.score} / {salary.max}</strong></div>
  </div>;
}

export default function App() {
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [candidateId, setCandidateId] = useState("");
  const [limit, setLimit] = useState("5");
  const [results, setResults] = useState<Recommendation[] | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [creatingCandidate, setCreatingCandidate] = useState(false);
  const [creatingJob, setCreatingJob] = useState(false);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const clearMessages = () => { setNotice(""); setError(""); };

  async function createCandidate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); clearMessages(); setCreatingCandidate(true);
    const form = new FormData(event.currentTarget);
    try {
      const created = await api.createCandidate({ name: form.get("name"), skills: splitSkills(String(form.get("skills"))), yearsOfExperience: Number(form.get("years")), location: form.get("location"), expectedSalary: Number(form.get("salary")) });
      setCandidate(created); setCandidateId(String(created.id)); setResults(null); setNotice(`Candidate created: ${created.name} (ID ${created.id}).`);
    } catch (requestError) { setError(messageFor(requestError)); } finally { setCreatingCandidate(false); }
  }

  async function createJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); clearMessages(); setCreatingJob(true);
    const form = new FormData(event.currentTarget);
    const requiredSkills = [...splitSkills(String(form.get("mustSkills"))).map((name) => ({ name, type: "must_have" })), ...splitSkills(String(form.get("niceSkills"))).map((name) => ({ name, type: "nice_to_have" }))];
    try {
      const created = await api.createJob({ title: form.get("title"), requiredSkills, minYearsExperience: Number(form.get("minYears")), location: form.get("jobLocation"), salaryRange: { min: Number(form.get("salaryMin")), max: Number(form.get("salaryMax")) }, remoteAllowed: form.get("remote") === "on" });
      setJob(created); setNotice(`Job created: ${created.title} (ID ${created.id}).`);
    } catch (requestError) { setError(messageFor(requestError)); } finally { setCreatingJob(false); }
  }

  async function loadRecommendations(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); clearMessages(); const id = Number(candidateId); const parsedLimit = Number(limit);
    if (!Number.isInteger(id) || id < 1 || !Number.isInteger(parsedLimit) || parsedLimit < 1 || parsedLimit > 100) { setError("Enter a positive candidate ID and a limit from 1 to 100."); return; }
    setLoadingRecommendations(true);
    try { const response = await api.recommendations(id, parsedLimit); setResults(response.results); } catch (requestError) { setResults(null); setError(messageFor(requestError)); } finally { setLoadingRecommendations(false); }
  }

  return <main>
    <header><p className="eyebrow">Job Match API · optional demo UI</p><h1>Transparent job recommendations</h1><p>Send profiles to the API and inspect its rule-based results.</p></header>
    {(notice || error) && <p className={`message ${error ? "error" : "success"}`}>{error || notice}</p>}
    <section className="grid">
      <form className="card" onSubmit={createCandidate}><h2>1. Create candidate</h2><label>Name<input name="name" required placeholder="Vanshika" /></label><label>Skills <small>Comma-separated</small><input name="skills" required placeholder="Python, FastAPI, PostgreSQL" /></label><label>Years of experience<input name="years" type="number" min="0" step="0.5" required defaultValue="2" /></label><label>Location<input name="location" required placeholder="Delhi" /></label><label>Expected salary<input name="salary" type="number" min="0" required placeholder="1200000" /></label><button disabled={creatingCandidate}>{creatingCandidate ? "Creating candidate..." : "Create candidate"}</button>{candidate && <p className="created">Active candidate: <strong>{candidate.name}</strong> · ID {candidate.id}</p>}</form>
      <form className="card" onSubmit={createJob}><h2>2. Create job</h2><label>Title<input name="title" required placeholder="Backend Engineer" /></label><label className="must">Must-have skills <small>Comma-separated</small><input name="mustSkills" required placeholder="Python, FastAPI" /></label><label className="nice">Nice-to-have skills <small>Optional, comma-separated</small><input name="niceSkills" placeholder="Docker, AWS" /></label><label>Minimum experience<input name="minYears" type="number" min="0" step="0.5" required defaultValue="2" /></label><label>Location<input name="jobLocation" required placeholder="Bangalore" /></label><div className="two"><label>Salary minimum<input name="salaryMin" type="number" min="0" required /></label><label>Salary maximum<input name="salaryMax" type="number" min="0" required /></label></div><label className="checkbox"><input name="remote" type="checkbox" /> Remote allowed</label><button disabled={creatingJob}>{creatingJob ? "Creating job..." : "Create job"}</button>{job && <p className="created">Created job: <strong>{job.title}</strong> · ID {job.id}</p>}</form>
    </section>
    <section className="recommendations card"><h2>3. Job recommendations</h2><form className="recommendation-form" onSubmit={loadRecommendations}><label>Candidate ID<input value={candidateId} onChange={(event) => setCandidateId(event.target.value)} inputMode="numeric" placeholder="Created candidate ID" required /></label><label>Limit<input value={limit} onChange={(event) => setLimit(event.target.value)} inputMode="numeric" required /></label><button disabled={loadingRecommendations}>{loadingRecommendations ? "Loading recommendations..." : "Load recommendations"}</button></form>{results?.length === 0 && <p className="empty">No matching jobs found for this candidate.</p>}<div className="result-grid">{results?.map((recommendation, index) => <article className="result" key={recommendation.jobId}><div className="result-heading"><span>#{index + 1}</span><h3>{recommendation.title}</h3><strong>{recommendation.score.toFixed(2)} <small>/ 100</small></strong></div><ScoreBreakdown recommendation={recommendation} /></article>)}</div></section>
  </main>;
}
