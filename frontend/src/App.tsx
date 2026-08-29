import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Route, Switch, useLocation, Router as WouterRouter } from 'wouter';
import { AboutPage, HomePage, HowItWorksPage } from '@/pages/public';
import { AdminDashboardPage, DistrictsPage, PredictionsPage, ProgramImpactPage, SkillDemandPage } from '@/pages/operations';
import { TraineeDashboardPage, TraineeGapPage, TraineeJobsPage, TraineeProfilePage, TraineeRecommendationsPage, TraineeSkillsPage, TraineeTrainingPage } from '@/pages/trainee';
import { AuthPage, EmployerDashboardPage, EmployerJobsPage, InstituteDashboardPage, InstituteProgramsPage } from '@/pages/roles';
import { AuthProvider } from '@/contexts/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function Router() {
  return (
    <RoutedErrorBoundary>
      <Switch>
        <Route path="/" component={HomePage} />
        <Route path="/about" component={AboutPage} />
        <Route path="/how-it-works" component={HowItWorksPage} />
        <Route path="/login"><AuthPage mode="login" /></Route>
        <Route path="/register"><AuthPage mode="register" /></Route>
        <Route path="/admin/dashboard" component={AdminDashboardPage} />
        <Route path="/admin/districts" component={DistrictsPage} />
        <Route path="/admin/skill-demand" component={SkillDemandPage} />
        <Route path="/admin/predictions" component={PredictionsPage} />
        <Route path="/admin/program-impact" component={ProgramImpactPage} />
        <Route path="/trainee/dashboard" component={TraineeDashboardPage} />
        <Route path="/trainee/profile" component={TraineeProfilePage} />
        <Route path="/trainee/skills" component={TraineeSkillsPage} />
        <Route path="/trainee/skill-gap" component={TraineeGapPage} />
        <Route path="/trainee/jobs" component={TraineeJobsPage} />
        <Route path="/trainee/training" component={TraineeTrainingPage} />
        <Route path="/trainee/recommendations" component={TraineeRecommendationsPage} />
        <Route path="/employer/dashboard" component={EmployerDashboardPage} />
        <Route path="/employer/jobs" component={EmployerJobsPage} />
        <Route path="/institute/dashboard" component={InstituteDashboardPage} />
        <Route path="/institute/programs" component={InstituteProgramsPage} />
        <Route component={NotFound} />
      </Switch>
    </RoutedErrorBoundary>
  );
}

function RoutedErrorBoundary({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
            <Router />
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
