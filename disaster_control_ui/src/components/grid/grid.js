import React, { useState, useEffect } from 'react';
import './grid.css';

export function Grid() {
  const [buttonColors, setButtonColors] = useState(
    Array(100).fill('lightblue')
  );

  const [selectedRadioValue, setSelectedRadioValue] = useState('low');

  //1 for available, user can drop a disaster, else if availability is 0 then there is already an active disaster
  const [availablity, setAvailablity] = useState(1);

  async function generateMap() {
    const mapData = {
      map_size: ["10", "10"]
    };
  
    const requestMap = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mapData)
    };
    
    //'http://127.0.0.1:8000/map/generate'

    try {
      const response = await fetch('http://127.0.0.1:8000/map/generate', requestMap);
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.log(error);
    }
  }

  async function generateStations() {
    const requestStations = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    };
    
    try {
      const response = await fetch('http://127.0.0.1:8000/map/generate/stations/4', requestStations);
      const finalData = await response.json();
      // Access the world_map array
      const worldMap = finalData.world_map;
      console.log(worldMap);

      // Access the station_coordinates array
      const stationCoordinates = finalData.station_coordinates;
      console.log(stationCoordinates);
      
      //draws out the map with new color
      const newButtonColors = Array(100).fill('lightblue');
      for (let i = 0; i < worldMap.length; i++) {
        const row = worldMap[i];
        for (let j = 0; j < row.length; j++) {
          const value = row[j];
          const index = i * 10 + j;
          if (value === 1) {
            newButtonColors[index] = 'lightblue';
          } else if (value === 2) {
            newButtonColors[index] = 'darkblue';
          } else if (value === 3) {
            newButtonColors[index] = '#964B00';
          }
        }
      }
      setButtonColors(newButtonColors);

    } catch (error) {
      console.log(error);
    }
  }

   //Generate the map and stations first
   useEffect(() => {
    async function generateData() {
      await generateMap();
      await generateStations();
    }
    generateData();
  }, []);



  const handleRadioChange = (e) => {
    setSelectedRadioValue(e.target.value);
  };

  async function handleFetch(x, y, threatLevel) {
    try {

      //the data is passed as (y,x)
      const disasterData = {
        disaster_coordinates: [String(y), String(x)],
        disaster_level: threatLevel
      };

      const response = await fetch(`http://127.0.0.1:8000/map/generate/disaster`, {
        method: 'POST',
        body: JSON.stringify(disasterData),
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      console.log(data);

      //Separating the path coordinates from the data
      const Coords = data.response[1];
      
      const pathCoords = JSON.parse(Coords); // parse the string back into objects
      console.log(pathCoords);

      let i = 1; // Start from the second index
      const intervalId = setInterval(() => {
        if (i >= pathCoords.length) {
          clearInterval(intervalId); // Stop the interval when all blocks are colored
          setAvailablity(1); //After path is complete, disaster is resolved user can now add a new disaster
          return;
        }

        const [row, col] = pathCoords[i];
        const buttonIndex = row * 10 + col;

        setButtonColors(prevColors => {
          const newColors = [...prevColors];
          newColors[buttonIndex] = 'lime';
          return newColors;
        });

        setTimeout(() => {
          setButtonColors(prevColors => {
            const newColors = [...prevColors];
            newColors[buttonIndex] = 'lightblue';
            return newColors;
          });
        }, 1000);

        i++;
      }, 1000);

     
    } catch (error) {
      console.error(error);
      return null;
    }
  }

  const handleClick = (index, x, y) => {
    if (availablity === 0) {
      console.log(
        'Cannot Add a new disaster, there is already an ongoing disaster. Please wait'
      );
      return;
    }

    if (buttonColors[index] !== 'lightblue') {
      return;
    }

    //Active disaster in progress
    setAvailablity(0);

    setButtonColors((prevColors) => {
      const newColors = [...prevColors];
      switch (selectedRadioValue) {
        case 'low':
          newColors[index] = 'yellow';
          //make a low status request
          handleFetch(x, y, 1);
          break;
        case 'moderate':
          newColors[index] = 'orange';
          //make a medium status request
          handleFetch(x, y, 2);
          break;
        case 'severe':
          newColors[index] = 'red';
          //make a high status request
          handleFetch(x, y, 3);
          break;
        default:
          newColors[index] = 'lightblue';
          break;
      }

      return newColors;
    });
  };

  return (
    <div className="container">
      <div className="radio-container">
        <h3>Severity Level</h3>
        <label>
          <input
            type="radio"
            name="color"
            value="low"
            checked={selectedRadioValue === 'low'}
            onChange={handleRadioChange}
          />
          Low
        </label>
        <label>
          <input
            type="radio"
            name="color"
            value="moderate"
            checked={selectedRadioValue === 'moderate'}
            onChange={handleRadioChange}
          />
          Moderate
        </label>
        <label>
          <input
            type="radio"
            name="color"
            value="severe"
            checked={selectedRadioValue === 'severe'}
            onChange={handleRadioChange}
          />
          Critical
        </label>
      </div>
      <table>
        <tbody>
          {Array.from({ length: 10 }, (_, row) => (
            <tr key={row}>
              {Array.from({ length: 10 }, (_, col) => {
                const index = row * 10 + col;
                const x = index % 10;
                const y = Math.floor(index / 10);
                return (
                  <td key={col}>
                    <button
                      className="square-button"
                      style={{ backgroundColor: buttonColors[index] }}
                      onClick={() => handleClick(index, x, y)}
                    ></button>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
