import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const token = localStorage.getItem('token');

  // Если есть токен, но еще загружаются данные пользователя - показываем загрузку
  if (token && loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        color: 'white',
        fontSize: '18px'
      }}>
        Загрузка...
      </div>
    );
  }

  // Если нет токена или нет пользователя (и не загружается) - редирект на логин
  if (!token || (!user && !loading)) {
    return <Navigate to="/login" replace />;
  }

  // Если есть токен и пользователь - показываем контент
  if (token && user) {
    return children;
  }

  // По умолчанию - загрузка
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      color: 'white',
      fontSize: '18px'
    }}>
      Загрузка...
    </div>
  );
};

export default ProtectedRoute;

