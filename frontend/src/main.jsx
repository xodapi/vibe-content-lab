import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const api = import.meta.env.VITE_API_URL || "";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [searching, setSearching] = useState(false);
  const [form, setForm] = useState({ type: "text", model: "", prompt: "" });
  const [estimate, setEstimate] = useState(null);
  const [message, setMessage] = useState("");

  async function askKnowledge(event) {
    event.preventDefault();
    setSearching(true);
    setAnswer(null);
    try {
      const response = await fetch(`${api}/api/knowledge/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      setAnswer(await response.json());
    } finally {
      setSearching(false);
    }
  }

  async function requestEstimate(event) {
    event.preventDefault();
    setMessage("");
    const response = await fetch(`${api}/api/generations/estimate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const result = await response.json();
    if (!response.ok) return setMessage(result.detail || "Не удалось получить смету.");
    setEstimate(result);
  }

  async function confirmGeneration() {
    const response = await fetch(
      `${api}/api/generations/${estimate.estimate_id}/confirm`,
      { method: "POST" },
    );
    const result = await response.json();
    setMessage(response.ok ? `Запрос отправлен: ${result.id}` : result.detail);
    if (response.ok) setEstimate(null);
  }

  return (
    <main>
      <header>
        <p className="eyebrow">INTERNAL AI TOOL · HUMAN-IN-THE-LOOP</p>
        <h1>Vibe Content Lab</h1>
        <p>RAG по публичной документации, смета до списания и явное подтверждение генерации.</p>
      </header>

      <section>
        <h2>Документация API</h2>
        <form onSubmit={askKnowledge}>
          <label>Вопрос
            <input value={question} onChange={(e) => setQuestion(e.target.value)}
              placeholder="Как работает idempotency_key?" required />
          </label>
          <button disabled={searching}>{searching ? "Ищу…" : "Спросить"}</button>
        </form>
        {answer?.answer && <article className="answer"><p>{answer.answer}</p>
          <h3>Источники</h3>
          <ol>{answer.sources.map((source, i) => <li key={i}><a href={source.source_url}>{source.section}</a></li>)}</ol>
        </article>}
        {answer?.detail && <p className="error">{answer.detail}</p>}
      </section>

      <section>
        <h2>Генерация с контролем бюджета</h2>
        <form onSubmit={requestEstimate}>
          <label>Тип
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              <option value="text">Текст</option><option value="image">Изображение</option>
              <option value="video">Видео</option><option value="voice">Озвучка</option>
              <option value="music">Музыка</option>
            </select>
          </label>
          <label>Модель
            <input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })}
              placeholder="Значение из /capabilities" required />
          </label>
          <label>Задание
            <textarea value={form.prompt} onChange={(e) => setForm({ ...form, prompt: e.target.value })}
              placeholder="Опишите креатив" required />
          </label>
          <button>Получить бесплатную смету</button>
        </form>
        {estimate && <aside>
          <strong>Смета: {estimate.estimated_cost_rub ?? "уточняется"} ₽</strong>
          <p>Проверьте параметры. Списание произойдёт только после этого действия.</p>
          <button className="danger" onClick={confirmGeneration}>Подтвердить генерацию</button>
        </aside>}
        {message && <p className="message">{message}</p>}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
