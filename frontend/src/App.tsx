import React, { useState } from 'react';
import axios from 'axios';
import NorthIndianChart from './NorthIndianChart';
import './App.css';

interface BirthData {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  latitude: number;
  longitude: number;
}

interface PlanetData {
  longitude: number;
  sign: string;
  degrees_in_sign: number;
  nakshatra: string;
  pada: number;
}

interface Kundali {
  ayanamsa: number;
  ayanamsa_type: string;
  tz_offset: number;
  ascendant: { longitude: number; sign: string };
  houses: number[];
  midheaven: number;
  planets: { [key: string]: PlanetData };
}

interface Navamsa {
  [key: string]: { navamsa_sign: string; navamsa_sign_index: number };
}

interface ChartResponse {
  kundali: Kundali;
  navamsa: Navamsa;
}

const App: React.FC = () => {
  const [birthData, setBirthData] = useState<BirthData>({
    year: 1990,
    month: 5,
    day: 15,
    hour: 10,
    minute: 30,
    latitude: 28.6669,
    longitude: 77.2169,
  });
  const [charts, setCharts] = useState<ChartResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setBirthData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/charts', birthData);
      setCharts(response.data);
    } catch (err) {
      setError('Failed to fetch charts. Is the backend running?');
    }
  };

  return (
    <div className="app-container">
      <div className="form-section">
        <h1 className="form-title">Vedic Astrology Calculator</h1>
        <form onSubmit={handleSubmit} className="form">
          <div className="form-grid">
            <input type="number" name="year" value={birthData.year} onChange={handleChange} placeholder="Year" className="form-input" />
            <input type="number" name="month" value={birthData.month} onChange={handleChange} placeholder="Month" className="form-input" />
            <input type="number" name="day" value={birthData.day} onChange={handleChange} placeholder="Day" className="form-input" />
            <input type="number" name="hour" value={birthData.hour} onChange={handleChange} placeholder="Hour (0-23)" className="form-input" />
            <input type="number" name="minute" value={birthData.minute} onChange={handleChange} placeholder="Minute (0-59)" className="form-input" />
            <input type="number" name="latitude" value={birthData.latitude} onChange={handleChange} placeholder="Latitude" className="form-input" step="0.0001" />
            <input type="number" name="longitude" value={birthData.longitude} onChange={handleChange} placeholder="Longitude" className="form-input" step="0.0001" />
          </div>
          <button type="submit" className="submit-button">Calculate Charts</button>
        </form>
        {error && <p className="error-message">{error}</p>}
      </div>

      {charts && (
        <div className="chart-grid">
          <div className="chart-column">
            <div className="chart-container">
              <h2 className="chart-title">Rasi Chart</h2>
              <NorthIndianChart
                planets={charts.kundali.planets}
                ascendant={charts.kundali.ascendant}
                houses={charts.kundali.houses}
              />
            </div>
            <div className="chart-container">
              <h2 className="chart-title">Navamsa Chart</h2>
              <NorthIndianChart
                planets={Object.fromEntries(
                  Object.entries(charts.navamsa).map(([planet, data]) => [
                    planet,
                    {
                      longitude: data.navamsa_sign_index * 30 + (charts.kundali.planets[planet]?.degrees_in_sign || 0),
                      sign: data.navamsa_sign,
                      degrees_in_sign: charts.kundali.planets[planet]?.degrees_in_sign || 0,
                      nakshatra: charts.kundali.planets[planet]?.nakshatra || '',
                      pada: charts.kundali.planets[planet]?.pada || 0,
                    }
                  ])
                )}
                ascendant={charts.kundali.ascendant}
                houses={charts.kundali.houses}
                navamsa={charts.navamsa}
              />
            </div>
          </div>

          <div>
            <h2 className="table-title">Planet Details</h2>
            <table className="table">
              <thead>
                <tr>
                  <th>Planet</th>
                  <th>Sign</th>
                  <th>Longitude</th>
                  <th>Nakshatra</th>
                  <th>Pada</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(charts.kundali.planets).map(([planet, data]) => (
                  <tr key={planet}>
                    <td>{planet}</td>
                    <td>{data.sign}</td>
                    <td>{data.longitude.toFixed(2)}°</td>
                    <td>{data.nakshatra}</td>
                    <td>{data.pada}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;