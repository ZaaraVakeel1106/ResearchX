import { useEffect, useState } from "react";

import { PaperDiscovery } from "./components/PaperDiscovery";
import { getHealth } from "./services/api";

type ApiState = "checking" | "online" | "offline";

function App() {
  const [apiState, setApiState] = useState<ApiState>("checking");

  useEffect(() => {
    let active = true;

    getHealth()
      .then(() => active && setApiState("online"))
      .catch(() => active && setApiState("offline"));

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="wordmark" href="#top" aria-label="Research X home">
          <span className="mark" aria-hidden="true">R<span>×</span></span>
          <span>Research <b>X</b></span>
        </a>
        <div className={`api-status api-status--${apiState}`} role="status">
          <span className="status-dot" aria-hidden="true" />
          {apiState === "checking" && "Connecting to API"}
          {apiState === "online" && "API connected"}
          {apiState === "offline" && "API unavailable"}
        </div>
      </header>

      <section className="hero" id="top" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow"><span /> A clearer path through the literature</p>
          <h1 id="hero-title">Good research<br />starts with <em>connection.</em></h1>
          <p className="tagline">Discover research. Connect ideas. Trace evidence.</p>
          <p className="intro">
            Follow the ideas behind a question, see how studies relate, and keep the evidence in view as you explore.
          </p>
          <a className="explore-link" href="#search">
            Discover papers <span aria-hidden="true">↘</span>
          </a>
        </div>

        <div className="map-card" aria-label="Illustration of connected research ideas">
          <div className="map-heading"><span>IDEAS IN RELATION</span><span>01 — 03</span></div>
          <svg className="idea-map" viewBox="0 0 580 430" role="img" aria-labelledby="map-title map-desc">
            <title id="map-title">A map of connected ideas</title>
            <desc id="map-desc">Three research themes connected by lines to evidence and a central question.</desc>
            <path className="thread thread-muted" d="M115 109 C195 107 200 187 284 209 S393 304 466 320" />
            <path className="thread" d="M115 109 C194 116 202 224 285 210 S378 123 455 99" />
            <path className="thread thread-muted" d="M455 99 C390 145 369 268 466 320" />
            <path className="thread thread-accent" d="M115 109 C182 190 220 220 285 210 S373 188 455 99" />
            <g className="map-node node-one"><circle r="7" /><circle className="orbit" r="17" /></g>
            <g className="map-node node-two"><circle r="7" /><circle className="orbit" r="17" /></g>
            <g className="map-node node-three"><circle r="7" /><circle className="orbit" r="17" /></g>
            <g className="map-node node-center"><circle r="11" /><circle className="orbit" r="25" /></g>
            <g className="map-node node-four"><circle r="7" /><circle className="orbit" r="17" /></g>
            <text className="node-label" x="66" y="70">01 / QUESTION</text>
            <text className="node-label" x="407" y="64">02 / METHODS</text>
            <text className="node-label" x="414" y="368">03 / EVIDENCE</text>
            <text className="center-label" x="218" y="263">A connected view</text>
          </svg>
          <div className="map-footer"><span>Start from a question</span><span>Follow what supports it&nbsp; ↗</span></div>
        </div>
        <div className="hero-index" aria-hidden="true">RESEARCH, MADE TRACEABLE <span>✳</span> VOL. 01</div>
      </section>

      <PaperDiscovery />

      <section className="approach" id="approach" aria-label="Research X principles">
        <div className="approach-intro">
          <span className="section-number">01 / THE APPROACH</span>
          <h2>Move through research<br />with <em>more context.</em></h2>
        </div>
        <article className="principle">
          <span className="principle-mark">↗</span>
          <h3>Follow connections</h3>
          <p>See the paths between questions, publications, and the ideas they share.</p>
        </article>
        <article className="principle">
          <span className="principle-mark">◎</span>
          <h3>Keep evidence close</h3>
          <p>Make it easier to trace a claim back to the research that supports it.</p>
        </article>
      </section>

      <footer className="footer"><span>Research X</span><span>Curiosity, with a clear trail.</span><span>© 2026</span></footer>
    </main>
  );
}

export default App;
