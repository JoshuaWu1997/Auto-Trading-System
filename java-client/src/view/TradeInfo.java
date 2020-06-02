package view;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.JButton;

public class TradeInfo extends JFrame {

	private static final long serialVersionUID = 1L;
	public JTable table;
	public JButton createFile;
	public JButton backToMain;
	public Object[][] tableContent;
	public String[] tableTitle = new String[] { "��Ʊ����", "��������ʱ��", "�ɽ���", "����", "�ɽ��۸�" };
	public boolean[] tableColumnEditables = new boolean[] { false, false, false, false, false };

	/**
	 * Create the frame.
	 */
	public TradeInfo() {
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setBounds(100, 100, 800, 400);
		JPanel contentPane = new JPanel();
		contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
		setContentPane(contentPane);
		contentPane.setLayout(null);

		JScrollPane scrollPane = new JScrollPane();
		scrollPane.setBounds(10, 10, 764, 260);
		contentPane.add(scrollPane);

		table = new JTable();
		table.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
		table.setColumnSelectionAllowed(true);
		table.setCellSelectionEnabled(true);
		scrollPane.setViewportView(table);

		createFile = new JButton("\u5BFC\u51FA\u62A5\u8868*");
		createFile.setBounds(260, 313, 93, 23);
		contentPane.add(createFile);

		backToMain = new JButton("\u8FD4\u56DE\u4E3B\u754C\u9762");
		backToMain.setBounds(430, 313, 100, 23);
		contentPane.add(backToMain);
	}
}
