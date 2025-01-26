import { IconType } from "react-icons";
import "./ActionButton.css";

type ActionButtonParams = {
  Icon: IconType;
  onClickHandler: () => void;
};

const ActionButton = ({ Icon, onClickHandler }: ActionButtonParams) => {
  return (
    <div className="action-button-container">
      <button onClick={onClickHandler} className="action-button">
        <Icon className="action-icon" />
      </button>
    </div>
  );
};

export default ActionButton;
