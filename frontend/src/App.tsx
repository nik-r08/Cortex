import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import DocumentList from './pages/DocumentList'
import DocumentDetail from './pages/DocumentDetail'
import Search from './pages/Search'
import FileUpload from './components/FileUpload'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <nav className="bg-white dark:bg-gray-800 border-b dark:border-gray-700 px-6 py-3 flex items-center gap-6">
          <h1 className="text-xl font-semibold dark:text-white">Cortex</h1>
          <NavLink to="/" className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900">Dashboard</NavLink>
          <NavLink to="/documents" className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900">Documents</NavLink>
          <NavLink to="/search" className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900">Search</NavLink>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<FileUpload onSuccess={() => window.location.href = '/documents'} />} />
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
