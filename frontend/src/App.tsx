/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** App
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Homepage from './pages/HomePage';
import Services from './pages/Services';
import ServiceDetail from './pages/ServiceDetail';
import Areaction from './pages/Areaction';
import About from './pages/About';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Profile from './pages/Profile';
import ResetPassword from './pages/ResetPassword';
import ForgotPassword from './pages/ForgotPassword';
import OAuthCallback from './pages/OAuthCallback';
import GitHubAppCallback from './pages/GitHubAppCallback';
import Debug from './pages/Debug';
import Navbar from './components/Navbar';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/homepage" element={<Homepage />} />
        <Route path="/services" element={<Services />} />
        <Route path="/services/:serviceId" element={<ServiceDetail />} />
        <Route path="/Areaction" element={<Areaction />} />
        <Route path="/about" element={<About />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/debug" element={<Debug />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/callback/:provider" element={<OAuthCallback />} />
        <Route path="/auth/github-app/callback" element={<GitHubAppCallback />} />
        <Route path="/setup/github-app" element={<GitHubAppCallback />} />
        <Route index element={<Homepage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
