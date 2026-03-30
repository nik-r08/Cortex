import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b px-6 py-3">
          <h1 className="text-xl font-semibold">Cortex</h1>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<div>Dashboard</div>} />
            <Route path="/upload" element={<div>Upload</div>} />
            <Route path="/documents/:id" element={<div>Document Detail</div>} />
            <Route path="/search" element={<div>Search</div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
