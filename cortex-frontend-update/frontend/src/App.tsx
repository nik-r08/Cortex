import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import DocumentList from './pages/DocumentList'
import DocumentDetail from './pages/DocumentDetail'
import Search from './pages/Search'
import Upload from './pages/Upload'

function navClass({ isActive }: { isActive: boolean }) {
  return `text-sm transition-colors ${
    isActive ? 'text-gray-900 font-medium' : 'text-gray-500 hover:text-gray-700'
  }`
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b px-6 py-3 flex items-center gap-8">
          <NavLink to="/" className="text-lg font-semibold text-gray-900 tracking-tight">
            Cortex
          </NavLink>
          <div className="flex items-center gap-6">
            <NavLink to="/" end className={navClass}>Dashboard</NavLink>
            <NavLink to="/documents" className={navClass}>Documents</NavLink>
            <NavLink to="/search" className={navClass}>Search</NavLink>
          </div>
        </nav>
        <main className="max-w-5xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/documents" element={<DocumentList />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/search" element={<Search />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
