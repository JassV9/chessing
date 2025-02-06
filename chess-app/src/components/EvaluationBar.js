import React from "react";
import styled from "styled-components";
import { motion } from "framer-motion";

const BarContainer = styled.div`
  width: 30px;
  height: 600px;
  background-color: #404040;
  margin: 20px 0;
  position: relative;
  overflow: hidden;
`;

const Indicator = styled(motion.div)`
  width: 100%;
  background: ${(props) => (props.advantage > 0 ? "white" : "black")};
  position: absolute;
  bottom: ${(props) => (props.advantage > 0 ? 0 : "auto")};
  top: ${(props) => (props.advantage <= 0 ? 0 : "auto")};
`;

const EvalText = styled.div`
  position: absolute;
  top: 10px;
  width: 100%;
  text-align: center;
  color: white;
  font-size: 12px;
  z-index: 1;
`;

const EvaluationBar = ({ evaluation }) => {
  const evalVariants = {
    initial: { height: "50%" },
    animate: {
      height: `${50 + evaluation * 10}%`,
      transition: { duration: 0.5, ease: "easeOut" },
    },
  };

  return (
    <BarContainer>
      <EvalText>
        {evaluation > 0 ? `+${evaluation.toFixed(1)}` : evaluation.toFixed(1)}
      </EvalText>
      <Indicator
        variants={evalVariants}
        initial="initial"
        animate="animate"
        advantage={evaluation}
      />
    </BarContainer>
  );
};

export default EvaluationBar;
