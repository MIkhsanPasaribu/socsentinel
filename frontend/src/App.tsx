/** SOCsentinel — Root application component. */

import { RouterProvider } from "react-router-dom";
import { Providers } from "./core/providers/Providers";
import { router } from "./core/router/router";
import { ToastProvider } from "./shared/components/Toast";

function App() {
  return (
    <Providers>
      <ToastProvider>
        <RouterProvider router={router} />
      </ToastProvider>
    </Providers>
  );
}

export default App;
