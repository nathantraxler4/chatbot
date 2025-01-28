import "./App.css";
import ChatWindow from "./components/ChatWindow";
import { useState, useEffect } from "react";
import { createClient, Session } from "@supabase/supabase-js";
import { Auth } from "@supabase/auth-ui-react";
import { ThemeSupa } from "@supabase/auth-ui-shared";

// TODO move these to environment variables.
// Supabase Public Anon key is safe for now in the browser: https://supabase.com/docs/guides/database/secure-data
const supabase = createClient(
  "https://odibndcpahnyzbmtnggu.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kaWJuZGNwYWhueXpibXRuZ2d1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4MzM5NjksImV4cCI6MjA1MzQwOTk2OX0.Q0NNFthZauCHyguwDUG6E6Kf2YYRQ6eLx6tbGTYxfcg"
);

export default function AuthWrapper() {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Override Supabase Auth theme
  if (ThemeSupa.default?.colors) {
    const brandColor = "#7f40f2";
    ThemeSupa.default.colors.brand = brandColor;
    ThemeSupa.default.colors.brandAccent = brandColor;
  }

  if (!session) {
    return <Auth supabaseClient={supabase} appearance={{ theme: ThemeSupa }} />;
  } else {
    return (
      <>
        <ChatWindow session={session} />
      </>
    );
  }
}
