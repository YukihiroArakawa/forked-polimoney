import { BoardMetadata } from '@/components/BoardMetadata';
import { BoardSummary } from '@/components/BoardSummary';
import { BoardTransactions } from '@/components/BoardTransactions';
import { Footer } from '@/components/Footer';
import { Header } from '@/components/Header';
import { Notice } from '@/components/Notice';
import data from '@/data/demo-example';
import { Box } from '@chakra-ui/react';

export default async function Page() {
  const reportData = data.datas[0];
  const otherReports = data.datas.map((d) => d.report);

  return (
    <Box>
      <Header />
      <BoardSummary
        profile={data.profile}
        report={reportData.report}
        otherReports={otherReports}
        flows={reportData.flows}
      />
      <BoardTransactions
        direction={'income'}
        total={reportData.report.totalIncome}
        transactions={reportData.transactions.filter(
          (t) => t.direction === '収入',
        )}
        showPurpose={true}
        showDate={true}
      />
      <BoardTransactions
        direction={'expense'}
        total={reportData.report.totalExpense}
        transactions={reportData.transactions.filter(
          (t) => t.direction === '支出',
        )}
        showPurpose={true}
        showDate={true}
      />
      <BoardMetadata report={reportData.report} />
      <Notice />
      <Footer />
    </Box>
  );
}
