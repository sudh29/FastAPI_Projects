import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Register from './components/register';
import Dashboard from './components/dashboard';
import Login from './components/login';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
