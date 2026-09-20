import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import CourseList from './pages/CourseList'
import CourseDetail from './pages/CourseDetail'
import AIAssistant from './pages/AIAssistant'
import Analytics from './pages/Analytics'
import AdminDashboard from './pages/AdminDashboard'
import KnowledgeGraph from './pages/KnowledgeGraph'
import StudyMaterials from './pages/StudyMaterials'
import Assignments from './pages/Assignments'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/courses" element={
            <ProtectedRoute><CourseList /></ProtectedRoute>
          } />
          <Route path="/courses/:courseId" element={
            <ProtectedRoute><CourseDetail /></ProtectedRoute>
          } />
          <Route path="/courses/:courseId/graph" element={
            <ProtectedRoute><KnowledgeGraph /></ProtectedRoute>
          } />
          <Route path="/courses/:courseId/assignments" element={
            <ProtectedRoute><Assignments /></ProtectedRoute>
          } />
          <Route path="/materials/:materialId/study" element={
            <ProtectedRoute><StudyMaterials /></ProtectedRoute>
          } />
          <Route path="/assistant" element={
            <ProtectedRoute roles={['student']}><AIAssistant /></ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute roles={['student']}><Analytics /></ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute roles={['faculty', 'admin']}><AdminDashboard /></ProtectedRoute>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="border-t border-ink/10 py-6 text-center text-xs text-ink/40">
        Athenaeum — AI-Powered Intelligent E-Learning Platform
      </footer>
    </div>
  )
}
