import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      logout();
      navigate('/login');
    } catch (error) {
      console.error('Ошибка выхода:', error);
    }
  };

  if (!user) {
    return null;
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <div className="dashboard-header">
          <h1>Профиль пользователя</h1>
          <button onClick={handleLogout} className="logout-button">
            Выйти
          </button>
        </div>
        <div className="user-info">
          <div className="info-item">
            <span className="info-label">Имя:</span>
            <span className="info-value">{user.first_name}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Фамилия:</span>
            <span className="info-value">{user.last_name}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Email:</span>
            <span className="info-value">{user.email}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Роль:</span>
            <span className="info-value">{user.role || 'user'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Дата регистрации:</span>
            <span className="info-value">{formatDate(user.created_at)}</span>
          </div>
        </div>
        <div className="welcome-message">
          <p>Добро пожаловать, {user.first_name} {user.last_name}!</p>
          <p>Вы успешно вошли в систему.</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

