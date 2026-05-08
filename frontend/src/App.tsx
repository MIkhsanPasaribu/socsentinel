/** SOCsentinel — Root application component. */

import { BrowserRouter } from "react-router-dom";
import { Providers } from "./core/providers/Providers";
import { AppRoutes } from "./core/router/router";
import { ToastProvider } from "./shared/components/Toast";

function App() {
  return (
    <Providers>
      <BrowserRouter>
        <ToastProvider>
          <AppRoutes />
        </ToastProvider>
      </BrowserRouter>
    </Providers>
  );
}

export default App;
