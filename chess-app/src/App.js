import React, { useState, useEffect } from "react";
import styled from "styled-components";
import ChessBoard from "./components/Board";
import EvaluationBar from "./components/EvaluationBar";
import Controls from "./components/Controls";
import { Container } from "./styles/StyledComponents";
import { initializeBoard, isValidMove, makeMove } from "./utils/chessLogic";
import {
  getMoveFromStockfish,
  getEvaluation,
  initializeStockfish,
} from "./utils/stockfishService";
import "./styles/global.css";

const Board = styled.div`
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  width: 600px;
  height: 600px;
  border: 2px solid #404040;
  margin: 20px;
`;

const Square = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${(props) =>
    props.selected
      ? "#fadb5f"
      : (props.row + props.col) % 2 === 0
      ? "#eeeed2"
      : "#769656"};
  cursor: pointer;
  font-size: 2.5em;
`;

const EvalBar = styled.div`
  width: 30px;
  height: 600px;
  background-color: #404040;
  margin: 20px 0;
  position: relative;
  overflow: hidden;
`;

const EvalIndicator = styled.div`
  width: 100%;
  background: ${(props) => (props.advantage > 0 ? "white" : "black")};
  position: absolute;
  bottom: ${(props) => (props.advantage > 0 ? 0 : "auto")};
  top: ${(props) => (props.advantage <= 0 ? 0 : "auto")};
`;

function App() {
  const [board, setBoard] = useState(initializeBoard());
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [evaluation, setEvaluation] = useState(0);
  const [vsAI, setVsAI] = useState(false);
  const [aiVsAi, setAiVsAi] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState("w");
  const [moveHistory, setMoveHistory] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [stockfishReady, setStockfishReady] = useState(false);

  useEffect(() => {
    const initStockfish = async () => {
      try {
        await initializeStockfish();
        setStockfishReady(true);
      } catch (error) {
        console.error("Failed to initialize Stockfish:", error);
      }
    };

    initStockfish();
  }, []);

  useEffect(() => {
    if (
      stockfishReady &&
      ((vsAI && currentPlayer === "b") || (aiVsAi && !isThinking))
    ) {
      makeAIMove();
    }
  }, [currentPlayer, vsAI, aiVsAi, stockfishReady]);

  const makeAIMove = async () => {
    if (isThinking) return;

    setIsThinking(true);
    try {
      const aiMove = await getMoveFromStockfish(board);
      if (aiMove) {
        const newBoard = makeMove(board, aiMove.from, aiMove.to);
        setBoard(newBoard);
        setCurrentPlayer(currentPlayer === "w" ? "b" : "w");
        const evaluation = await getEvaluation(newBoard);
        setEvaluation(evaluation);
        setMoveHistory([...moveHistory, { from: aiMove.from, to: aiMove.to }]);
      }
    } catch (error) {
      console.error("AI move error:", error);
    }
    setIsThinking(false);
  };

  const handleSquareClick = (row, col) => {
    if (vsAI && currentPlayer === "b") return; // Prevent moves during AI turn
    if (aiVsAi) return; // Prevent moves during AI vs AI

    if (!selectedSquare) {
      const piece = board[row][col];
      if (piece && piece.color === currentPlayer) {
        setSelectedSquare({ row, col });
      }
    } else {
      const to = { row, col };
      if (isValidMove(board, selectedSquare, to, currentPlayer)) {
        const newBoard = makeMove(board, selectedSquare, to);
        setBoard(newBoard);
        setCurrentPlayer(currentPlayer === "w" ? "b" : "w");
        setMoveHistory([...moveHistory, { from: selectedSquare, to }]);
      }
      setSelectedSquare(null);
    }
  };

  const handleNewGame = () => {
    setBoard(initializeBoard());
    setSelectedSquare(null);
    setCurrentPlayer("w");
    setMoveHistory([]);
    setEvaluation(0);
    setIsThinking(false);
  };

  const handleToggleAI = () => {
    setVsAI(!vsAI);
    setAiVsAi(false);
  };

  const handleToggleAIvsAI = () => {
    setAiVsAi(!aiVsAi);
    setVsAI(false);
  };

  return (
    <Container>
      <ChessBoard
        board={board}
        selectedSquare={selectedSquare}
        onSquareClick={handleSquareClick}
      />
      <EvaluationBar evaluation={evaluation} />
      <Controls
        onNewGame={handleNewGame}
        onToggleAI={handleToggleAI}
        onToggleAIvsAI={handleToggleAIvsAI}
        vsAI={vsAI}
        aiVsAi={aiVsAi}
      />
    </Container>
  );
}

export default App;
