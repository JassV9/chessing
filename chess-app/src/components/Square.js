import React from "react";
import styled from "styled-components";

const SquareContainer = styled.div`
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
  transition: background-color 0.2s;

  &:hover {
    filter: brightness(1.1);
  }
`;

const Square = ({ row, col, piece, selected, onClick }) => {
  return (
    <SquareContainer row={row} col={col} selected={selected} onClick={onClick}>
      {piece}
    </SquareContainer>
  );
};

export default Square;
