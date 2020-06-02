package view;

import controller.ViewController;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JButton;
import javax.swing.ListSelectionModel;
import java.io.IOException;

public class MainUI extends JFrame {

    private static final long serialVersionUID = 1L;
    public JPanel contentPane;
    public JTable table;
    public JButton resumeItem;
    public JButton createItem;
    public JButton checkItem;
    public JButton exit;
    public Object[][] tableContent;
    public String[] tableTitle = new String[]{"ID", "Start Time", "End Time", "Initial Cash", "Current Cash", "Total Asset", "Status"};
    public boolean[] tableColumnEditables = new boolean[]{false, false, false, false, false, false, false};

    public static void main(String[] args) throws IOException {
        MainUI frame = new MainUI();
        frame.setVisible(true);
        ViewController controller = new ViewController(frame);
        controller.setMainUIAction();
    }

    /**
     * Create the frame.
     */
    public MainUI() {
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 1000, 400);
        contentPane = new JPanel();
        contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
        setContentPane(contentPane);
        contentPane.setLayout(null);

        JScrollPane scrollPane = new JScrollPane();
        scrollPane.setBounds(10, 10, 964, 200);
        contentPane.add(scrollPane);

        table = new JTable();
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        table.setColumnSelectionAllowed(true);
        table.setCellSelectionEnabled(true);
        scrollPane.setViewportView(table);

        checkItem = new JButton("check");
        checkItem.setEnabled(false);
        checkItem.setBounds(240, 300, 100, 23);
        contentPane.add(checkItem);

        resumeItem = new JButton("continue");
        resumeItem.setEnabled(false);
        resumeItem.setBounds(380, 300, 100, 23);
        contentPane.add(resumeItem);

        createItem = new JButton("new trade");
        createItem.setBounds(520, 300, 100, 23);
        contentPane.add(createItem);

        exit = new JButton("exit");
        exit.setBounds(660, 300, 100, 23);
        contentPane.add(exit);
    }
}
