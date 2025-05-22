import { Circle, Icon } from "@chakra-ui/react";
import { FaQuestionCircle } from "react-icons/fa";

interface FloatingChatButtonProps {
  onClick: () => void;
}

const FloatingChatButton = ({ onClick }: FloatingChatButtonProps) => {
  return (
    <Circle
      as="button"
      position="fixed"
      bottom="4"
      right="4"
      size="50px"
      bg="blue.500"
      color="white"
      boxShadow="lg"
      zIndex="overlay"
      onClick={onClick}
      _hover={{ bg: "blue.600" }}
      transition="all 0.2s"
      aria-label="Get help"
    >
      <Icon as={FaQuestionCircle} boxSize="24px" />
    </Circle>
  );
};

export default FloatingChatButton;