import { render, screen } from './test-utils';
import App from './App';

test('renders patent checker title', () => {
  render(<App />);
  const titleElement = screen.getByText(/Patent Infringement Checker/i);
  expect(titleElement).toBeInTheDocument();
});
