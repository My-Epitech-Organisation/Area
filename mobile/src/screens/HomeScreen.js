import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import {
  Button,
  Card,
  TextInput,
  Title,
  Paragraph,
  Text,
  ActivityIndicator,
  Chip,
  useTheme
} from 'react-native-paper';
const API_URL = 'http://10.172.116.56:8080';

const HomeScreen = ({ navigation }) => {
  const theme = useTheme();
  const [response, setResponse] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [city, setCity] = useState('Paris');
  const [loading, setLoading] = useState(false);
  const [textToTranslate, setTextToTranslate] = useState('');
  const [targetLang, setTargetLang] = useState('en');
  const [translationResult, setTranslationResult] = useState(null);
  const [translationLoading, setTranslationLoading] = useState(false);

  const handleButtonClick = async () => {
    try {
      const response = await fetch(`${API_URL}/api/trigger`, {
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
      const response = await fetch(`${API_URL}/api/weather?city=${city}`);

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setWeatherData(data);
    } catch (error) {
      console.error('Error fetching weather data:', error);
      setWeatherData({ error: 'Could not retrieve weather data' });
    } finally {
      setLoading(false);
    }
  };

  const handleTranslateButtonClick = async () => {
    if (!textToTranslate.trim()) {
      setTranslationResult({ error: 'Please enter text to translate' });
      return;
    }

    const words = textToTranslate.trim().split(/\\s+/);
    if (words.length > 1) {
      setTranslationResult({
        error: 'Due to API limitations, please translate one word at a time',
        originalText: textToTranslate,
        targetLang: targetLang
      });
      return;
    }

    setTranslationLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/translate`, {
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
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setTranslationResult(data);
    } catch (error) {
      console.error('Error during translation:', error);
      setTranslationResult({ error: 'Translation error' });
    } finally {
      setTranslationLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.title}>POC Action-Réaction</Title>

            <Button
              mode="contained"
              onPress={handleButtonClick}
              style={styles.button}
            >
              Trigger Action
            </Button>

            {response && (
              <View style={styles.responseContainer}>
                <Text>{response}</Text>
              </View>
            )}

            <View style={styles.section}>
              <Title style={styles.sectionTitle}>Weather</Title>
              <TextInput
                label="City"
                value={city}
                onChangeText={setCity}
                style={styles.input}
              />
              <Button
                mode="contained"
                onPress={handleWeatherButtonClick}
                loading={loading}
                style={[styles.button, { backgroundColor: '#EAB308' }]}
                icon="weather-partly-cloudy"
              >
                {loading ? 'Loading...' : 'Get Weather'}
              </Button>

              {weatherData && !weatherData.error && (
                <Card style={styles.weatherCard}>
                  <Card.Content>
                    <Title>{weatherData.city}</Title>
                    <Paragraph style={{ textTransform: 'capitalize' }}>{weatherData.description}</Paragraph>

                    <View style={styles.weatherGrid}>
                      <View style={styles.weatherItem}>
                        <Text style={styles.weatherLabel}>Temperature</Text>
                        <Text style={styles.weatherValue}>{weatherData.temperature}°C</Text>
                      </View>
                      <View style={styles.weatherItem}>
                        <Text style={styles.weatherLabel}>Feels Like</Text>
                        <Text style={styles.weatherValue}>{weatherData.feelsLike}°C</Text>
                      </View>
                      <View style={styles.weatherItem}>
                        <Text style={styles.weatherLabel}>Humidity</Text>
                        <Text style={styles.weatherValue}>{weatherData.humidity}%</Text>
                      </View>
                      <View style={styles.weatherItem}>
                        <Text style={styles.weatherLabel}>Wind</Text>
                        <Text style={styles.weatherValue}>{weatherData.windSpeed} m/s</Text>
                      </View>
                    </View>
                  </Card.Content>
                </Card>
              )}

              {weatherData && weatherData.error && (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{weatherData.error}</Text>
                </View>
              )}
            </View>

            <View style={styles.section}>
              <Title style={styles.sectionTitle}>Translator</Title>
              <Paragraph style={styles.note}>
                Note: Due to API limitations, please translate one word at a time.
              </Paragraph>

              <TextInput
                label="Text to translate"
                value={textToTranslate}
                onChangeText={setTextToTranslate}
                style={styles.input}
                multiline
              />

              <View style={styles.langSelector}>
                <Text>Target language:</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipContainer}>
                  {[
                    { label: 'English', value: 'en' },
                    { label: 'Spanish', value: 'es' },
                    { label: 'German', value: 'de' },
                    { label: 'Italian', value: 'it' },
                    { label: 'French', value: 'fr' },
                  ].map(lang => (
                    <Chip
                      key={lang.value}
                      selected={targetLang === lang.value}
                      onPress={() => setTargetLang(lang.value)}
                      style={styles.chip}
                    >
                      {lang.label}
                    </Chip>
                  ))}
                </ScrollView>
              </View>

              <Button
                mode="contained"
                onPress={handleTranslateButtonClick}
                loading={translationLoading}
                style={[styles.button, { backgroundColor: '#22C55E' }]}
                icon="translate"
              >
                {translationLoading ? 'Translating...' : 'Translate'}
              </Button>

              {translationResult && !translationResult.error && (
                <Card style={styles.translationCard}>
                  <Card.Content>
                    <Text style={styles.translationLabel}>Original text:</Text>
                    <Text style={styles.translationText}>{translationResult.originalText}</Text>

                    <Text style={styles.translationLabel}>
                      Translation ({translationResult.targetLang}):
                    </Text>
                    <Text style={styles.translationText}>
                      {translationResult.translatedText}
                    </Text>
                  </Card.Content>
                </Card>
              )}

              {translationResult && translationResult.error && (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{translationResult.error}</Text>
                </View>
              )}
            </View>

            <Button
              mode="outlined"
              onPress={() => navigation.navigate('UserList')}
              style={styles.navigationButton}
              icon="account-multiple"
            >
              Go to User Management
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#8B5CF6',
  },
  scrollContent: {
    padding: 16,
  },
  card: {
    marginVertical: 8,
    borderRadius: 12,
    elevation: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
    color: '#6366F1',
  },
  button: {
    marginVertical: 8,
    paddingVertical: 8,
  },
  navigationButton: {
    marginTop: 16,
  },
  responseContainer: {
    backgroundColor: '#D1FAE5',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  section: {
    marginTop: 24,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  sectionTitle: {
    fontSize: 20,
    marginBottom: 12,
    color: '#6366F1',
  },
  input: {
    marginBottom: 12,
    backgroundColor: 'white',
  },
  weatherCard: {
    marginTop: 12,
    backgroundColor: '#EFF6FF',
  },
  weatherGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 12,
  },
  weatherItem: {
    width: '50%',
    padding: 8,
  },
  weatherLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  weatherValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
  },
  errorText: {
    color: '#DC2626',
  },
  note: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 12,
    fontStyle: 'italic',
  },
  langSelector: {
    marginBottom: 12,
  },
  chipContainer: {
    flexDirection: 'row',
    marginTop: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  translationCard: {
    marginTop: 12,
    backgroundColor: '#ECFDF5',
  },
  translationLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  translationText: {
    fontSize: 16,
    marginBottom: 12,
  },
});

export default HomeScreen;
