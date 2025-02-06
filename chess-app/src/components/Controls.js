import React from "react";
import styled from "styled-components";

const ControlsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 20px;
`;

const Button = styled.button`
  padding: 10px 20px;
  background-color: #4a4a4a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  &:hover {
    background-color: #5a5a5a;
  }
`;

function Controls({ onNewGame, onToggleAI, onToggleAIvsAI, vsAI, aiVsAi }) {
  return (
    <ControlsContainer>
      <Button onClick={onNewGame}>New Game</Button>
      <Button onClick={onToggleAI}>
        {vsAI ? "Play vs Human" : "Play vs AI"}
      </Button>
      <Button onClick={onToggleAIvsAI}>
        {aiVsAi ? "Stop AI vs AI" : "Watch AI vs AI"}
      </Button>
    </ControlsContainer>
  );
}

export default Controls;
