import { Routes, Route } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { UploadPage } from './pages/UploadPage';
import { ResultsPage } from './pages/ResultsPage';

function App() {
  return (
    <div className="min-h-svh flex flex-col bg-[var(--bg)]">
      <Header />
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/jobs/:jobId" element={<ResultsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;