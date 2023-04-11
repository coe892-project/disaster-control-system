import React, { useState } from 'react';
import './grid.css';

export function Grid() {
  const [buttonColors, setButtonColors] = useState(
    Array(100).fill('lightblue')
  );
  const [selectedRadioValue, setSelectedRadioValue] = useState('low');

  //1 for available, user can drop a disaster, else if availability is 0 then there is already an active disaster
  const [availablity, setAvailablity] = useState(1);

  const handleRadioChange = (e) => {
    setSelectedRadioValue(e.target.value);
  };

  async function handleFetch(color, x, y) {
    try {
      const response = await fetch(`/api/${color}`, {
        method: 'POST',
        body: JSON.stringify({ x, y, color }),
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      return data;
      //if response is success, then
      if (data.status) {
        // change color back to light blue
        const index = data.y * 10 + data.x;
        setButtonColors((prevColors) => {
          const newColors = [...prevColors];
          newColors[index] = 'lightblue';
          return newColors;
        });
      }
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
          handleFetch('/api/low', { x, y, color: 'yellow' });
          break;
        case 'moderate':
          newColors[index] = 'orange';
          //make a medium status request
          handleFetch('/api/medium', { x, y, color: 'orange' });
          break;
        case 'severe':
          newColors[index] = 'red';
          //make a high status request
          handleFetch('/api/high', { x, y, color: 'red' });
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
