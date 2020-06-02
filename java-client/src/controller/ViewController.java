package controller;

import java.awt.Color;
import java.awt.Component;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.*;
import java.nio.charset.StandardCharsets;

import java.lang.System;
import java.net.Socket;
import java.util.TimerTask;
import java.util.Timer;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;

import org.apache.commons.io.FileUtils;
import org.jfree.data.category.DefaultCategoryDataset;

import view.MainUI;
import view.NewTradeUI;
import view.TradeInfo;
import view.TradeUI;

public class ViewController {
    private MainUI MainFrame;
    private NewTradeUI NewTradeFrame;
    private TradeInfo TradeInfoFrame;
    private TradeUI TradeFrame;
    private String TradeID;
    private DBConnector crawlerDB, userDB;
    private Timer TradeTimer;
    private String TradeTimeStamp = "";
    private String StartTimeStamp, EndTimeStamp;
    private Double BenchMark, InitialAsset;
    private Color[][] price_color;
    private String host;
    private int port;
    private Socket socket;
    private PrintStream out;
    private BufferedReader in;
    private String strategy;
    private int rows;


    public ViewController(MainUI frame) throws IOException {
        this.MainFrame = frame;
        crawlerDB = new DBConnector("crawlerdb", "root", "123456");
        userDB = new DBConnector("userdb", "root", "123456");
        String[] host_port = FileUtils.readFileToString(new File("setting.txt"), "utf-8").split(",");
        host = host_port[2];
        port = Integer.parseInt(host_port[3]);
    }


    private void setTable(JTable table, String[] tableTitle, Object[][] tableContent, boolean[] tableColumnEditables) {
        table.setModel(new DefaultTableModel(tableContent, tableTitle) {
            public boolean isCellEditable(int row, int column) {
                return tableColumnEditables[column];
            }
        });
    }


    private void newNewTradeUI() {
        NewTradeFrame = new NewTradeUI();
        setNewTradeBackToMain();
    }

    private void newTradeInfoUI() {
        TradeInfoFrame = new TradeInfo();
        initialiseTradeInfo();
        setTradeInfoExit();
    }

    private void newTradeUI() {
        StartTimeStamp = String.valueOf(MainFrame.table.getValueAt(MainFrame.table.getSelectedRow(), 1));
        EndTimeStamp = String.valueOf(MainFrame.table.getValueAt(MainFrame.table.getSelectedRow(), 2));
        InitialAsset = Double.valueOf(String.valueOf(MainFrame.table.getValueAt(MainFrame.table.getSelectedRow(), 5)));
        TradeFrame = new TradeUI();
        if (JOptionPane.showConfirmDialog(
                null,
                "Do you want to update market history data?",
                "please choose",
                JOptionPane.YES_NO_OPTION) == 0) addTradeGetHistory();
        initialiseTradeOrders();
        initialiseTradePosition();
        setTradeStop();
        setTradeStart();
        setTradeExit();
    }

    public void setMainUIAction() {
        initialiseMainData();
        addMainTableMouseListener();
        setMainExitAction();
        setMainCreateItem();
        setMainCheckItem();
        setMainResumeItem();
    }

    private void setNewTradeBackToMain() {
        NewTradeFrame.backToMain.addActionListener(arg0 -> {
            NewTradeFrame.setVisible(false);
            NewTradeFrame = null;
            MainFrame.setVisible(true);
        });
    }

    private void setMainExitAction() {
        MainFrame.exit.addActionListener(arg0 -> System.exit(0));
    }

    private void setMainCreateItem() {
        MainFrame.createItem.addActionListener(arg0 -> {
            MainFrame.setVisible(false);
            newNewTradeUI();
            NewTradeFrame.setVisible(true);
        });
    }

    private void setMainCheckItem() {
        MainFrame.checkItem.addActionListener(arg0 -> {
            MainFrame.setVisible(false);
            newTradeInfoUI();
            TradeInfoFrame.setVisible(true);
        });
    }

    private void setMainResumeItem() {
        MainFrame.resumeItem.addActionListener(arg0 -> {
            MainFrame.setVisible(false);
            newTradeUI();
            TradeFrame.setVisible(true);
        });
    }

    private void setTradeInfoExit() {
        TradeInfoFrame.backToMain.addActionListener(arg0 -> {
            TradeInfoFrame.setVisible(false);
            TradeInfoFrame = null;
            initialiseMainData();
            MainFrame.setVisible(true);
        });
    }

    private void setTradeStart() {
        TradeFrame.start.addActionListener(arg0 -> {
            TradeFrame.stop.setEnabled(true);
            TradeFrame.start.setEnabled(false);
            TradeFrame.complete.setEnabled(false);
            TradeFrame.backMain.setEnabled(false);
            addTradeBrokerStart();
        });
    }

    private void setTradeStop() {
        TradeFrame.stop.addActionListener(arg0 -> {
            try {
                out.println("over");
            } catch (Exception e) {
                e.printStackTrace();
            }
            TradeBrokerEnd();
        });
    }

    private void setTradeExit() {
        TradeFrame.backMain.addActionListener(arg0 -> {
            TradeFrame.setVisible(false);
            TradeFrame = null;
            initialiseMainData();
            MainFrame.setVisible(true);
        });
    }

    private void initialiseMainData() {
        MainFrame.checkItem.setEnabled(false);
        MainFrame.resumeItem.setEnabled(false);
        try {
            userDB.executeQuery("select count(*) from trade_list");
            userDB.rs.next();
            int rows = userDB.rs.getInt(1);
            MainFrame.tableContent = new Object[rows][9];
            userDB.executeQuery(
                    "select t_id,begin_datetime,end_datetime,begin_cash,valid_cash,total_asset,trade_state from trade_list"
            );
            for (int i = 0; i < rows; i++) {
                userDB.rs.next();
                for (int j = 0; j < 7; j++)
                    MainFrame.tableContent[i][j] = userDB.rs.getObject(j + 1);
            }
        } catch (Exception e) {
            System.out.println("initialiseMainData");
            e.printStackTrace();
        }
        setTable(MainFrame.table, MainFrame.tableTitle, MainFrame.tableContent, MainFrame.tableColumnEditables);
    }

    private void initialiseTradeInfo() {
        try {
            userDB.executeQuery("select count(*) from trade_detail where t_id=" + TradeID);
            userDB.rs.next();
            int rows = userDB.rs.getInt(1);
            TradeFrame.TradeHistory.setText("Trading History : " + rows);
            TradeInfoFrame.tableContent = new Object[rows][6];
            userDB.executeQuery("select stock_id,transaction_datetime,volume,direction,price "
                    + "from trade_detail where t_id=" + TradeID);
            for (int i = 0; i < rows; i++) {
                userDB.rs.next();
                for (int j = 0; j < 5; j++)
                    TradeInfoFrame.tableContent[i][j] = userDB.rs.getObject(j + 1);
            }
        } catch (Exception e) {
            System.out.println("initialiseTradeInfo");
            e.printStackTrace();
        }
        setTable(TradeInfoFrame.table, TradeInfoFrame.tableTitle, TradeInfoFrame.tableContent,
                TradeInfoFrame.tableColumnEditables);
    }

    private void refreshTradeMarket() {
        TradeFrame.MarketInfo.setText("Market Info : " + TradeTimeStamp);
        try {
            //Refresh the Portfolio Status Diagram
            crawlerDB.executeQuery(
                    "select price from crawl_data where datetime=\"" + TradeTimeStamp + "\" and id=\"sh000016\"");
            crawlerDB.rs.next();
            double CurrMark = crawlerDB.rs.getDouble(1);
            userDB.executeQuery(
                    "select total_asset from trade_list where t_id=" + TradeID);
            userDB.rs.next();
            double CurrAsset = userDB.rs.getDouble(1);
            Double MarketRatio = (CurrMark - BenchMark) / BenchMark;
            Double AssetRatio = (CurrAsset - InitialAsset) / InitialAsset;
            System.out.println("\nSH00016:\t" + MarketRatio.toString() + "\nCurrent Asset:\t" + AssetRatio.toString());
            TradeFrame.mDataset.removeColumn(0);
            TradeFrame.mDataset.addValue(MarketRatio, "SH50", TradeTimeStamp.substring(14));
            TradeFrame.mDataset.addValue(AssetRatio, "PnL", TradeTimeStamp.substring(14));
            TradeFrame.mPlot.setDataset(TradeFrame.mDataset);
            // Refresh the Market Info Chart
            System.out.println("Current Time:\t" + TradeTimeStamp);
            crawlerDB.executeQuery(
                    "select id,price,buy,sell,amount from crawl_data where datetime=\"" + TradeTimeStamp + "\"");
            Double PreValue, CurrValue;
            for (int i = 0; i < rows; i++) {
                crawlerDB.rs.next();
                for (int j = 1; j < 4; j++) {
                    PreValue = new Double(String.valueOf(TradeFrame.marketContent[i][j]));
                    TradeFrame.marketContent[i][j] = crawlerDB.rs.getObject(j + 1);
                    CurrValue = new Double(String.valueOf(TradeFrame.marketContent[i][j]));
                    int k = PreValue.compareTo(CurrValue);
                    price_color[i][j - 1] = k < 0 ? Color.RED : (k > 0 ? Color.GREEN : Color.WHITE);
                }
                TradeFrame.marketContent[i][0] = crawlerDB.rs.getObject(1);
                TradeFrame.marketContent[i][4] = crawlerDB.rs.getInt(5);
            }
            setTable(TradeFrame.market, TradeFrame.marketTitle, TradeFrame.marketContent, TradeFrame.marketColumnEditables);
            TradeFrame.market.setDefaultRenderer(Object.class, new BuySellRenderer(price_color));
        } catch (Exception e) {
            System.out.print("Market Info Error");
            e.printStackTrace();
        }
    }

    private void initialiseTradeOrders() {
        try {
            userDB.executeQuery("select count(*) from trade_detail where t_id=" + TradeID);
            userDB.rs.next();
            int rows = userDB.rs.getInt(1);
            TradeFrame.TradeHistory.setText("Trading History : " + rows);
            TradeFrame.ordersContent = new Object[rows][6];
            userDB.executeQuery(
                    "select stock_id,transaction_datetime,volume,direction,price " + "from trade_detail where t_id="
                            + TradeID + " order by transaction_datetime desc");
            for (int i = 0; i < rows; i++) {
                userDB.rs.next();
                for (int j = 0; j < 5; j++)
                    TradeFrame.ordersContent[i][j] = userDB.rs.getObject(j + 1);
            }
        } catch (Exception e) {
            System.out.println("initialiseTradeOrders");
            e.printStackTrace();
        }
        setTable(TradeFrame.orders, TradeFrame.ordersTitle, TradeFrame.ordersContent, TradeFrame.ordersColumnEditables);
    }

    private void initialiseTradePosition() {
        try {
            userDB.executeQuery("select count(*) from position where t_id=" + TradeID);
            userDB.rs.next();
            int rows = userDB.rs.getInt(1);
            TradeFrame.Position.setText("Position : " + rows);
            TradeFrame.positionContent = new Object[rows][2];
            userDB.executeQuery("select stock_id,volume " + "from position where t_id=" + TradeID + " order by stock_id");
            for (int i = 0; i < rows; i++) {
                userDB.rs.next();
                for (int j = 0; j < 2; j++)
                    TradeFrame.positionContent[i][j] = userDB.rs.getObject(j + 1);
            }
        } catch (Exception e) {
            System.out.println("initialiseTradePosition");
            e.printStackTrace();
        }
        setTable(TradeFrame.position, TradeFrame.positionTitle, TradeFrame.positionContent,
                TradeFrame.positionColumnEditables);
    }

    private void addMainTableMouseListener() {
        MainFrame.table.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent arg0) {
                strategy = String.valueOf(MainFrame.table.getValueAt(MainFrame.table.getSelectedRow(), 6));
                if (strategy.equals("finished")) {
                    MainFrame.checkItem.setEnabled(true);
                    MainFrame.resumeItem.setEnabled(false);
                } else {
                    MainFrame.resumeItem.setEnabled(true);
                    MainFrame.checkItem.setEnabled(false);
                }
                TradeID = MainFrame.table.getValueAt(MainFrame.table.getSelectedRow(), 0).toString();
            }
        });
    }

    private void TradeBrokerEnd() {
        try {
            TradeTimer.cancel();
            socket.close();
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        System.out.print("Trade broker ends.");
        TradeFrame.start.setEnabled(true);
        TradeFrame.complete.setEnabled(true);
        TradeFrame.backMain.setEnabled(true);
        TradeFrame.stop.setEnabled(false);
        TradeTimeStamp = "";
        TradeFrame.setTitle("Trade UI");
    }


    private void addTradeUITimer() {
        TradeTimer = new Timer();
        TradeTimer.schedule(new TimerTask() {
            public void run() {
                try {
                    String tmp = in.readLine();
                    if (tmp.endsWith("over") | tmp.endsWith("500")) throw new Exception("Received OVER or 500");
                    else {
                        out.print("received");
                        if (tmp.endsWith("sent")) {
                            tmp = tmp.replaceAll(",sent", "");
                            TradeTimeStamp = tmp;
                            System.out.println(tmp);
                            initialiseTradePosition();
                            initialiseTradeOrders();
                            refreshTradeMarket();
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    TradeBrokerEnd();
                }
            }
        }, 0, 100);
    }


    private void addTradeBrokerStart() {
        TradeFrame.setTitle("trading......");
        try {
            socket = new Socket(host, port);
            System.out.println("============ SERVER ADDRESS: host=> " + host + ", port=> " + port + " ============");
            out = new PrintStream(socket.getOutputStream());
            in = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            if (in.readLine().endsWith("start")) {
                out.print(strategy + "," + TradeID + "over");
                initialiseTradeMarket();
                addTradeUITimer();
            } else throw new Exception("Server did not respond.");
        } catch (Exception e) {
            e.printStackTrace();
            TradeBrokerEnd();
        }
    }

    private void initialiseTradeMarket() throws Exception {
        // Initialise start time
        if (strategy.endsWith("test") | strategy.endsWith("replay")) TradeTimeStamp = StartTimeStamp;
        else {
            crawlerDB.executeQuery(
                    "select MAX(datetime) from crawl_data");
            crawlerDB.rs.next();
            TradeTimeStamp = crawlerDB.rs.getString(1);
        }
        // Initialise stock list rows
        crawlerDB.executeQuery(
                "select count(*) from crawl_data where datetime=\"" + TradeTimeStamp + "\"");
        crawlerDB.rs.next();
        rows = crawlerDB.rs.getInt(1);
        // Initialise benchmark
        crawlerDB.executeQuery(
                "select price from crawl_data where datetime=\"" + TradeTimeStamp + "\" and id=\"sh000016\"");
        crawlerDB.rs.next();
        System.out.println("select price from crawl_data where datetime=\"" + TradeTimeStamp + "\" and id=\"sh000016\"");
        BenchMark = crawlerDB.rs.getDouble(1);
        TradeFrame.MarketInfo.setText("Market Info : " + TradeTimeStamp);
        System.out.println("\n------------------" + TradeTimeStamp + "------------------");
        System.out.println("SH00016:\t" + BenchMark.toString() + "\nCurrent Asset:\t" + InitialAsset.toString());
        // Initialise the Portfolio Status Diagram
        price_color = new Color[rows][3];
        TradeFrame.marketContent = new Object[rows][5];
        TradeFrame.mDataset = new DefaultCategoryDataset();
        for (int i = 0; i < 120; i++) {
            TradeFrame.mDataset.addValue(null, "PnL", Integer.toString(i));
            TradeFrame.mDataset.addValue(null, "SH50", Integer.toString(i));
        }
        // Initialise the Market Info Chart
        crawlerDB.executeQuery(
                "select id,price,buy,sell,amount from crawl_data where datetime=\"" + TradeTimeStamp + "\"");
        for (int i = 0; i < rows; i++) {
            crawlerDB.rs.next();
            for (int j = 0; j < 5; j++)
                TradeFrame.marketContent[i][j] = crawlerDB.rs.getObject(j + 1);
        }
        setTable(TradeFrame.market, TradeFrame.marketTitle, TradeFrame.marketContent, TradeFrame.marketColumnEditables);
    }

    private void addTradeGetHistory() {
        TradeFrame.setEnabled(false);
        TradeFrame.setVisible(true);
        TradeFrame.setTitle("getting history......");
        try {
            socket = new Socket(host, port);
            System.out.println("============ SERVER ADDRESS: host=> " + host + ", port=> " + port + " ============");
            out = new PrintStream(socket.getOutputStream());
            in = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            out.print("get_history," + "over");
            String tmp;
            while ((tmp = in.readLine()) != null) {
                if (tmp.equals("over")) break;
                System.out.println(tmp.replace(',', '\n'));
                if (tmp.equals("500")) break;
            }
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "python socket server is down");
            System.exit(-1);
        }
        TradeFrame.setEnabled(true);
        System.out.print("Getting history completed.");
        TradeFrame.setTitle("Trade UI");
    }
}

class BuySellRenderer implements TableCellRenderer {
    private Color[][] price_color;
    public static final DefaultTableCellRenderer DEFAULT_RENDERER = new DefaultTableCellRenderer();

    BuySellRenderer(Color[][] price_color) {
        this.price_color = price_color;
        DEFAULT_RENDERER.setHorizontalAlignment(SwingConstants.CENTER);
    }


    public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
        Component renderer = DEFAULT_RENDERER.getTableCellRendererComponent(table, value, isSelected, hasFocus, row,
                column);
        if (column > 0 && column < 4)
            renderer.setBackground(price_color[row][column - 1]);
        else
            renderer.setBackground(Color.white);
        return renderer;
    }
}

