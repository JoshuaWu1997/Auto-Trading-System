package view;

import java.awt.Color;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.category.DefaultCategoryDataset;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

public class NewTradeUI extends JFrame {

	private static final long serialVersionUID = 1L;
	public JPanel contentPane;
	public JFreeChart mChart;
	public CategoryDataset mDataset;
	public ChartPanel mChartPanel;
	public JButton begin;
	public JButton terminate;
	public JButton backToMain;

	/**
	 * Create the frame.
	 */
	public NewTradeUI() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 600, 450);
		contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		contentPane.setLayout(null);

		mDataset = GetDataset();
		mChart = ChartFactory.createLineChart("", "", "", mDataset, PlotOrientation.VERTICAL, false, false, false);
		CategoryPlot mPlot = (CategoryPlot) mChart.getPlot();
		mPlot.setBackgroundPaint(Color.LIGHT_GRAY);
		mPlot.setRangeGridlinePaint(Color.BLUE);// �����ײ�������
		mPlot.setOutlinePaint(Color.RED);// �߽���

		mChartPanel = new ChartPanel(mChart);
		mChartPanel.setMouseZoomable(false);
		mChartPanel.setMouseWheelEnabled(true);
		mChartPanel.setLocation(10, 10);
		mChartPanel.setSize(564, 240);
		contentPane.add(mChartPanel);
		mChartPanel.setLayout(null);

		begin = new JButton("\u5F00\u59CB\u8BAD\u7EC3*");
		begin.setBounds(140, 360, 93, 23);
		contentPane.add(begin);

		terminate = new JButton("\u505C\u6B62\u8BAD\u7EC3");
		terminate.setEnabled(false);
		terminate.setBounds(243, 360, 93, 23);
		contentPane.add(terminate);

		backToMain = new JButton("\u8FD4\u56DE\u4E3B\u754C\u9762");
		backToMain.setBounds(346, 360, 100, 23);
		contentPane.add(backToMain);
	}

	public static CategoryDataset GetDataset() {
		DefaultCategoryDataset mDataset = new DefaultCategoryDataset();
		mDataset.addValue(1, "First", "2013");
		mDataset.addValue(3, "First", "2014");
		mDataset.addValue(2, "First", "2015");
		mDataset.addValue(6, "First", "2016");
		mDataset.addValue(5, "First", "2017");
		mDataset.addValue(12, "First", "2018");
		mDataset.addValue(14, "Second", "2013");
		mDataset.addValue(13, "Second", "2014");
		mDataset.addValue(12, "Second", "2015");
		mDataset.addValue(9, "Second", "2016");
		mDataset.addValue(5, "Second", "2017");
		mDataset.addValue(7, "Second", "2018");
		return mDataset;
	}
}
