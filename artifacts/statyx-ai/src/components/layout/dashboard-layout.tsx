import { useAuth } from "@/hooks/use-auth";
import { useLogout } from "@workspace/api-client-react";
import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  LayoutDashboard, 
  UploadCloud, 
  Wand2, 
  BarChart3, 
  LineChart, 
  BrainCircuit, 
  Network, 
  FileText,
  LogOut,
  Menu
} from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useState } from "react";

const NAV_ITEMS = [
  { path: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { path: "/dashboard/analytics?page=upload", label: "Upload Data", icon: UploadCloud },
  { path: "/dashboard/analytics?page=clean", label: "Data Cleaning", icon: Wand2 },
  { path: "/dashboard/analytics?page=statistics", label: "Statistics", icon: BarChart3 },
  { path: "/dashboard/analytics?page=visualizations", label: "Visualizations", icon: LineChart },
  { path: "/dashboard/analytics?page=ai-analysis", label: "AI Analysis", icon: BrainCircuit },
  { path: "/dashboard/analytics?page=cross-tabulation", label: "Cross Tabulation", icon: Network },
  { path: "/dashboard/analytics?page=reports", label: "Reports", icon: FileText },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout: clearAuth } = useAuth();
  const logout = useLogout();
  const [location, setLocation] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout.mutate(undefined, {
      onSuccess: () => {
        clearAuth();
        setLocation("/login");
      }
    });
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-sidebar border-r border-sidebar-border">
      <div className="p-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg text-sidebar-foreground">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground shadow-sm">
            <BarChart3 size={18} />
          </div>
          Statyx AI
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          // A bit of custom logic to handle ?page= matching
          const isOverview = item.exact;
          let isActive = false;
          
          if (isOverview) {
            isActive = location === "/dashboard";
          } else {
            const searchParams = new URLSearchParams(window.location.search);
            const page = searchParams.get('page');
            const itemPage = new URLSearchParams(item.path.split('?')[1]).get('page');
            isActive = location.startsWith("/dashboard/analytics") && page === itemPage;
          }

          return (
            <Link 
              key={item.path} 
              href={item.path}
              onClick={() => setMobileMenuOpen(false)}
            >
              <div className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive 
                  ? "bg-sidebar-primary/10 text-sidebar-primary font-medium" 
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              }`}>
                <item.icon size={18} />
                <span>{item.label}</span>
              </div>
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 mb-4 px-2">
          <Avatar className="h-9 w-9 border border-border">
            <AvatarFallback className="bg-primary/5 text-primary">
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col overflow-hidden">
            <span className="text-sm font-medium truncate">{user?.name}</span>
            <span className="text-xs text-muted-foreground truncate">{user?.email}</span>
          </div>
        </div>
        <Button variant="outline" className="w-full justify-start text-muted-foreground hover:text-foreground" onClick={handleLogout}>
          <LogOut size={16} className="mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen w-full flex bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:block w-64 shrink-0 fixed inset-y-0 left-0 z-10">
        <SidebarContent />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col md:pl-64 min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden flex items-center justify-between p-4 border-b border-border bg-background sticky top-0 z-10">
          <div className="flex items-center gap-2 font-semibold">
            <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center text-primary-foreground">
              <BarChart3 size={18} />
            </div>
            Statyx AI
          </div>
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu size={20} />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-[280px]">
              <SidebarContent />
            </SheetContent>
          </Sheet>
        </header>

        <main className="flex-1 flex flex-col relative">
          {children}
        </main>
      </div>
    </div>
  );
}
