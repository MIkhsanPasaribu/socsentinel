/** SOCsentinel — Root application component. */

import { RouterProvider } from "react-router-dom";
import { Providers } from "./core/providers/Providers";
import { router } from "./core/router/router";

function App() {
  return (
    <Providers>
      <RouterProvider router={router} />
    </Providers>
  );
}

export default App;
