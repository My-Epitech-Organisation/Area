import React, { useState } from 'react';
import './App.css';

function App() {
  const [response, setResponse] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState('Paris');
  const [textToTranslate, setTextToTranslate] = useState('');
  const [targetLang, setTargetLang] = useState('en');
  const [translationResult, setTranslationResult] = useState(null);
  const [translationLoading, setTranslationLoading] = useState(false);

  const handleButtonClick = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      setResponse(data.message);
    } catch (error) {
      console.error('Erreur lors de la requête:', error);
      setResponse('Erreur de connexion au serveur');
    }
  };

  const handleWeatherButtonClick = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8080/api/weather?city=${city}`);

      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }

      const data = await response.json();
      setWeatherData(data);
    } catch (error) {
      console.error('Erreur lors de la récupération des données météo:', error);
      setWeatherData({ error: 'Impossible de récupérer les données météo' });
    } finally {
      setLoading(false);
    }
  };

  const handleTranslateButtonClick = async () => {
    if (!textToTranslate.trim()) {
      setTranslationResult({ error: 'Veuillez entrer un texte à traduire' });
      return;
    }

    const words = textToTranslate.trim().split(/\s+/);
    if (words.length > 1) {
      setTranslationResult({
        error: 'Pour des raisons de limitation de l\'API, veuillez traduire un seul mot à la fois',
        originalText: textToTranslate,
        targetLang: targetLang
      });
      return;
    }

    setTranslationLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textToTranslate,
          targetLang: targetLang,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }

      const data = await response.json();
      setTranslationResult(data);
    } catch (error) {
      console.error('Erreur lors de la traduction:', error);
      setTranslationResult({ error: 'Erreur lors de la traduction' });
    } finally {
      setTranslationLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="w-full max-w-md p-8 mx-auto bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-2xl border border-white border-opacity-20">
        <h1 className="text-3xl font-bold text-indigo-600 mb-8 text-center">
          POC Action-Réaction
        </h1>
        <button
          onClick={handleButtonClick}
          className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 mb-4"
        >
          Déclencher une action
        </button>
        {response && (
          <div className="mt-2 mb-4 p-4 bg-green-100 text-green-800 rounded-md">
            {response}
          </div>
        )}
        <div className="mt-4 mb-4">
          <div className="flex items-center mb-2">
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Entrez une ville"
              className="flex-1 p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </div>
          <button
            onClick={handleWeatherButtonClick}
            disabled={loading}
            className="w-full flex items-center justify-center bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
          >
            <span className="mr-2 text-2xl">☀️</span>
            {loading ? 'Chargement...' : 'Météo'}
          </button>
        </div>
        {weatherData && !weatherData.error && (
          <div className="mt-4 p-4 bg-blue-50 text-blue-800 rounded-md">
            <div className="flex items-center mb-2">
              <img
                src={`http://openweathermap.org/img/wn/${weatherData.icon}@2x.png`}
                alt={weatherData.description}
                className="w-16 h-16 mr-2"
              />
              <div>
                <h3 className="text-xl font-bold">{weatherData.city}</h3>
                <p className="capitalize">{weatherData.description}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Température</p>
                <p className="text-lg font-bold">{weatherData.temperature}°C</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Ressenti</p>
                <p className="text-lg font-bold">{weatherData.feelsLike}°C</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Humidité</p>
                <p className="text-lg font-bold">{weatherData.humidity}%</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Vent</p>
                <p className="text-lg font-bold">{weatherData.windSpeed} m/s</p>
              </div>
            </div>
          </div>
        )}
        {weatherData && weatherData.error && (
          <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-md">
            {weatherData.error}
          </div>
        )}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h2 className="text-xl font-bold text-indigo-600 mb-4">
            Traducteur
          </h2>
          <p className="text-sm text-gray-500 mb-2">
            Note: Pour des raisons de limitation de l'API, veuillez traduire un seul mot à la fois.
          </p>
          <div className="mb-4">
            <textarea
              value={textToTranslate}
              onChange={(e) => setTextToTranslate(e.target.value)}
              placeholder="Entrez le texte à traduire"
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-400 min-h-[100px]"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Langue cible:</label>
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              <option value="en">Anglais</option>
              <option value="es">Espagnol</option>
              <option value="de">Allemand</option>
              <option value="it">Italien</option>
              <option value="fr">Français</option>
            </select>
          </div>
          <button
            onClick={handleTranslateButtonClick}
            disabled={translationLoading}
            className="w-full flex items-center justify-center bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
          >
            <span className="mr-2 text-2xl">🌐</span>
            {translationLoading ? 'Traduction en cours...' : 'Traduire'}
          </button>
          {translationResult && !translationResult.error && (
            <div className="mt-4 p-4 bg-green-50 text-green-800 rounded-md">
              <div className="mb-2">
                <p className="text-sm text-gray-500">Texte original:</p>
                <p className="font-medium">{translationResult.originalText}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Traduction ({translationResult.targetLang}):</p>
                <p className="font-bold">{translationResult.translatedText}</p>
              </div>
            </div>
          )}
          {translationResult && translationResult.error && (
            <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-md">
              {translationResult.error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
