%% Gráficas en pdf 
clear
close all
clc
% File's route
txt_file = 'C:\Users\jabac\OneDrive - Universidad del Norte\Documentos\Tareas\Proyecto final\Scripts\Repositorio\Proyecto-Final\Versión 2022-01\Results\Op_Diagram.txt';
% Data table
data_table = readtable(txt_file);
% Diagram dimensions
width = 8.5;    %for a ieee paper
height = 5.3;   %for a ieee paper
% Figure setup
x0=2*2.54;
y0=1*2.54;
f1 = figure('Units','centimeters',...
            'Position',[0 0 width height],...
            'PaperPositionMode','auto');
a = plot(seconds(data_table.Time1), data_table.Distance);
hold on
b = plot(seconds(data_table.Time2), data_table.Distance);
c = plot(seconds(data_table.Time3), data_table.Distance);
d = plot(seconds(data_table.Time4), data_table.Distance);
e = plot(seconds(data_table.Time5), data_table.Distance);
f = plot(seconds(data_table.Time6), data_table.Distance);
g = plot(seconds(data_table.Time7), data_table.Distance);
grid on
set(gca,'Units','normalized',...
'Position',[.15 .2 .75 .7],...
'FontUnits','points',...
'FontWeight','normal',...
'FontSize',8,...
'FontName','Times',...
'GridLineStyle',':',...
'GridColor','k',...
'GridAlpha',0.5,...
'ylim',[0, 17], ...
'xlim',[seconds(21600), seconds(28800)])
xtickformat('hh:mm')

leg = legend('$Bus_1$','$Bus_2$','$Bus_3$','$Bus_4$','$Bus_5$','$Bus_6$','$Bus_7$');
set(leg,'FontUnits','points',...
'FontWeight','normal',...
'FontSize',7,...
'FontName','Times',...
'Location','best',...
'Orientation','Vertical',...
'box','off',...
'Interpreter','latex')

ylabel('Distance [km]',...
'FontUnits','points',...
'FontWeight','normal',...
'FontSize',8,...
'FontName','Times',...
'Interpreter','latex')

xlabel('Time [h]',...
'FontUnits','points',...
'FontWeight','normal',...
'FontSize',8,...
'FontName','Times',...
'Interpreter','latex')


set(f1,'PaperUnits','centimeters','PaperSize',[width height]); %set the paper size to what you want  
print(f1,'Op_diagram.pdf','-dpdf') % then print it