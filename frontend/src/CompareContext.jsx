import { createContext, useContext, useEffect, useState } from "react";

const Ctx = createContext(null);
export const useCompare = () => useContext(Ctx);

// Keeps the ids of apartments chosen for comparison (max 3), remembered in sessionStorage.
export function CompareProvider({ children }) {
  const [ids, setIds] = useState(() => JSON.parse(sessionStorage.getItem("rw_compare") || "[]"));
  useEffect(() => sessionStorage.setItem("rw_compare", JSON.stringify(ids)), [ids]);

  const toggle = (id) => {
    if (ids.includes(id)) return setIds(ids.filter((x) => x !== id));
    if (ids.length >= 3) return alert("You can compare up to 3 apartments.");
    setIds([...ids, id]);
  };
  return <Ctx.Provider value={{ ids, toggle, clear: () => setIds([]), has: (id) => ids.includes(id) }}>{children}</Ctx.Provider>;
}
