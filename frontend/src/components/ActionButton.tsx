import { IconType } from "react-icons";
import "./ActionButton.css";

type ActionButtonParams = { Icon: IconType };

const ActionButton = ({ Icon }: ActionButtonParams) => {
  return (
    <div className="action-button-container">
      <button className="action-button">
        <Icon className="action-icon" />
      </button>
    </div>
  );
};

export default ActionButton;
