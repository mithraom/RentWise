export const Loading = ({ text = "Loading..." }) => <div className="state"><div className="spinner" />{text}</div>;
export const ErrorBox = ({ message, onRetry }) => (
  <div className="state error">⚠️ {message}{onRetry && <button className="btn small" onClick={onRetry}>Retry</button>}</div>
);
export const Empty = ({ children }) => <div className="empty">{children}</div>;
